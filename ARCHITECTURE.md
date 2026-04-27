# CodeRAG — Technical Architecture

This document describes the internal design of CodeRAG in detail: how the subsystems fit together, the data flow from ingestion to response, and the design decisions behind each component.

---

## High-Level Data Flow

```
            ┌──────────────────────────────┐
            │      Source Material         │
            │  (GitHub URL / ZIP / Files)  │
            └──────────────┬───────────────┘
                           │
                    [ ingest.py / UI ]
                           │
            ┌──────────────▼───────────────┐
            │        DataIngestor          │
            │  src/ingestion/document_     │
            │  loaders.py                  │
            │                              │
            │  • Code files                │
            │  • Markdown / README         │
            │  • PDFs (pdfplumber)         │
            │  • Diagrams (Pillow)         │
            │  • Text chunking             │
            └──────────────┬───────────────┘
                           │ List[Document]
              ┌────────────┴────────────┐
              │                         │
   ┌──────────▼──────────┐   ┌──────────▼──────────┐
   │  VectorStoreManager  │   │  SparseStoreManager  │
   │  src/indexing/       │   │  src/indexing/       │
   │  vector_store.py     │   │  sparse_store.py     │
   │                      │   │                      │
   │  HuggingFace embeds  │   │  BM25 (rank_bm25)    │
   │  → FAISS index       │   │  → Pickle index      │
   └──────────────────────┘   └──────────────────────┘
              │                         │
              └───────────┬─────────────┘
                          │  Saved to workspace/
                          │
            ┌─────────────▼────────────────┐
            │         At Query Time         │
            │       HybridRetriever         │
            │   src/retrieval/hybrid_       │
            │   search.py                   │
            │                               │
            │  1. Rewrite query             │
            │  2. Multi-query expand        │
            │  3. HYDE generation           │
            │  4. FAISS search              │
            │  5. BM25 search               │
            │  6. Merge + deduplicate       │
            │  7. Cross-encoder rerank      │
            │  8. Context compression       │
            └─────────────┬─────────────────┘
                          │ Top-K chunks
            ┌─────────────▼─────────────────┐
            │      Generation Module         │
            │   src/generation/             │
            │                               │
            │  Build prompt with context    │
            │  → Groq LLM (langchain-groq)  │
            │  → Response + source cites    │
            └───────────────────────────────┘
```

---

## Component Reference

### `src/ingestion/document_loaders.py` — DataIngestor

**Purpose:** Discovers files in the data directory (or a provided repo), loads their content, and splits it into overlapping chunks suitable for embedding.

**Supported file types:**

| Type | Loader | Notes |
|---|---|---|
| Code (`.py`, `.js`, `.ts`, `.java`, etc.) | LangChain `TextLoader` | Language-aware chunking preserves function/class boundaries |
| Markdown (`.md`) | LangChain `TextLoader` | Header-aware splitting |
| PDF | `pdfplumber` | Page-level extraction |
| Images / Diagrams | `Pillow` | Caption/filename metadata extracted |

**Output:** `List[Document]` where each `Document` carries:
- `page_content` — the text chunk
- `metadata` — source path, file type, chunk index

---

### `src/indexing/vector_store.py` — VectorStoreManager

**Purpose:** Takes the document list and builds a FAISS vector index.

**Process:**
1. Loads HuggingFace embedding model (configurable via `config/`)
2. Encodes all document chunks into dense vectors
3. Builds a FAISS `IndexFlatL2` (or `IndexIVFFlat` for large corpora)
4. Saves index + docstore to `vector_store/` (or workspace path)

**Key methods:**
- `build_and_save(documents)` — full build from scratch
- `load()` — reload an existing index for querying

---

### `src/indexing/sparse_store.py` — SparseStoreManager

**Purpose:** Builds a BM25 keyword index alongside the FAISS dense index.

**Process:**
1. Tokenizes document chunks
2. Builds a `BM25Okapi` model (from `rank_bm25`)
3. Serializes the model and corpus to disk as a pickle

**Key methods:**
- `build_and_save(documents)` — build and persist
- `load()` — reload for querying

BM25 complements FAISS well because it excels at exact keyword matches (e.g., a function name like `handleAuthCallback`) that dense embeddings may rank lower.

---

### `src/retrieval/hybrid_search.py` — HybridRetriever

This is the core of CodeRAG's retrieval quality. The retrieval process runs in stages:

#### Stage 1 — Query Rewriting
The user's raw query is rephrased to be more retrieval-friendly (e.g., removing conversational filler).

#### Stage 2 — Multi-Query Expansion
Three to five alternative phrasings of the query are generated via LLM. This improves recall by catching documents that respond to one framing but not another.

#### Stage 3 — HYDE (Hypothetical Document Embeddings)
A hypothetical answer to the question is generated first. The *embedding of that hypothetical answer* is used as an additional search vector, which tends to improve precision for code-specific queries.

#### Stage 4 — Hybrid Search
Both FAISS and BM25 are queried with all expanded queries. Results are pooled and deduplicated by source chunk.

#### Stage 5 — Cross-Encoder Reranking
Retrieved candidates are reranked by a cross-encoder model (which scores query+chunk pairs jointly). This catches cases where the bi-encoder similarity score was misleading.

#### Stage 6 — Context Compression
The top-K reranked chunks are passed through a context compressor that strips irrelevant sentences from each chunk before they are sent to the LLM, reducing noise and prompt length.

**Return value:** `(List[Document], debug_trace)` — the trace contains per-stage metadata useful for debugging retrieval quality.

---

### `src/generation/` — Generation Module

**Purpose:** Assembles the final prompt from the compressed context chunks and calls the Groq LLM.

The prompt template instructs the model to:
- Answer only from the provided context
- Cite specific source files for claims
- Acknowledge when information is not found in the context

**LLM integration:** Uses `langchain-groq` with configurable model name (e.g., `llama3-8b-8192`, `mixtral-8x7b-32768`).

---

### `src/workspace_manager.py` — WorkspaceManager

**Purpose:** Manages the filesystem namespace for each project.

Each workspace is a subdirectory containing:
```
projects/<workspace_name>/
    faiss_index/         ← FAISS index files
    bm25_index.pkl       ← BM25 pickle
    metadata.json        ← project info (name, created, last ingested)
    chat_history.json    ← conversation turns
```

**Key methods:**
- `create_workspace(name)` — initialize directory structure
- `get_projects()` → list all workspace names
- `get_workspace_path(name)` → resolve paths for a project

---

### `src/chat_manager.py` — ChatManager

**Purpose:** Maintains per-session conversation history and provides the `ask()` interface that orchestrates retrieval + generation.

Stores messages as `[{"role": "user"|"assistant", "content": "..."}]` and passes recent history as context to the LLM so follow-up questions work correctly.

---

### `evaluation/metrics.py` — StandardMetrics

**Purpose:** Computes standard IR metrics against ground-truth data.

| Method | Description |
|---|---|
| `calculate_precision_at_k(retrieved, expected, k)` | What fraction of the top-K docs are relevant? |
| `calculate_recall_at_k(retrieved, expected, k)` | What fraction of all relevant docs appear in top-K? |
| `calculate_mrr(retrieved, expected)` | What is the reciprocal rank of the first relevant doc? |

---

## Configuration

`config/` holds YAML or Python config files for:
- Embedding model name
- Chunk size / overlap
- Top-K retrieval count
- Reranker model name
- Groq model name

These can be modified to tune performance without touching source code.

---

## Workspace Isolation

Every project runs in complete isolation. Creating two workspaces for `repo-A` and `repo-B` means separate FAISS indexes, separate BM25 models, and separate chat histories. The UI lets users switch between workspaces freely.

---

## Deployment Notes

When deploying to Streamlit Cloud:
- `GROQ_API_KEY` must be set as a Secret
- The `vector_store/` directory is ephemeral unless backed by persistent storage
- For persistent workspaces across deployments, consider mounting an external volume or using cloud storage for index files
