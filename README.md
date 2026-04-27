<div align="center">

# 🔍 CodeRAG

### Developer Knowledge Assistant — Ask Questions About Any Codebase

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-red?logo=streamlit)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-RAG-green)](https://www.langchain.com/)
[![Groq](https://img.shields.io/badge/Groq-LLM-orange)](https://groq.com/)
[![FAISS](https://img.shields.io/badge/FAISS-Vector%20Search-blueviolet)](https://faiss.ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**[Live Demo →](https://code-rag.streamlit.app/)**

</div>

---

CodeRAG is an **Advanced Retrieval-Augmented Generation (RAG) system** that lets developers explore and understand large codebases through natural language. Ingest any GitHub repository, then ask questions like *"Where is authentication handled?"* or *"Explain the overall architecture"* — and get grounded, source-cited answers powered by a hybrid search pipeline and Groq LLMs.

---

## ✨ Features

- **Natural Language Querying** — Ask anything about a codebase in plain English
- **Hybrid Retrieval** — Combines FAISS dense vector search with BM25 keyword search for best-of-both coverage
- **Advanced RAG Techniques** — Multi-query generation, HYDE (Hypothetical Document Embeddings), Cross-Encoder reranking, and context compression
- **Multi-Source Ingestion** — Supports code files, Markdown docs, PDFs, and architecture diagrams
- **Workspace Isolation** — Each project lives in its own workspace with independent indexes and chat history
- **Source Citations** — Every answer links back to the exact files and chunks it was drawn from
- **Built-in Evaluation** — Measures retrieval quality with Precision@K, Recall@K, and MRR

---

## 🏗️ Architecture Overview

```
User Query
    │
    ▼
┌─────────────────────────────────────────────────┐
│               Retrieval Pipeline                │
│                                                 │
│  1. Query Rewriting                             │
│  2. Multi-Query Generation                      │
│  3. HYDE Document Synthesis                     │
│  4. Hybrid Search (FAISS + BM25)                │
│  5. Cross-Encoder Reranking                     │
│  6. Context Compression                         │
└──────────────────────┬──────────────────────────┘
                       │ Top-K Chunks
                       ▼
┌─────────────────────────────────────────────────┐
│             Generation (Groq LLM)               │
│  Context-grounded answer + source citations     │
└─────────────────────────────────────────────────┘
```

The system has four main subsystems:

| Subsystem | Responsibility |
|---|---|
| **Ingestion** (`src/ingestion/`) | Loads files, parses code/docs/PDFs/images, splits into chunks |
| **Indexing** (`src/indexing/`) | Builds FAISS dense index and BM25 sparse index per workspace |
| **Retrieval** (`src/retrieval/`) | Hybrid search, reranking, context filtering |
| **Generation** (`src/generation/`) | Prompt construction, Groq LLM call, response formatting |

---

## 📁 Project Structure

```
codeRAG/
│
├── app.py                        # Streamlit entry point
├── ingest.py                     # CLI ingestion script (legacy/batch)
├── evaluate.py                   # CLI evaluation runner
│
├── src/
│   ├── ingestion/
│   │   └── document_loaders.py   # DataIngestor — loads code, docs, PDFs, diagrams
│   ├── indexing/
│   │   ├── vector_store.py       # VectorStoreManager — FAISS index build/load
│   │   └── sparse_store.py       # SparseStoreManager — BM25 index build/load
│   ├── retrieval/
│   │   └── hybrid_search.py      # HybridRetriever — combined search + reranking
│   ├── generation/
│   │   └── (LLM chain, prompt templates)
│   ├── workspace_manager.py      # WorkspaceManager — project isolation logic
│   └── chat_manager.py           # ChatManager — conversation history & session state
│
├── evaluation/
│   ├── eval_dataset.json         # Ground-truth Q&A pairs for evaluation
│   └── metrics.py                # StandardMetrics — Precision@K, Recall@K, MRR
│
├── ui/                           # Streamlit UI components
├── config/                       # Configuration files
├── data/                         # Drop source files here for ingestion
├── vector_store/                 # Generated FAISS indexes (gitignored)
├── .streamlit/                   # Streamlit theme/config
├── .devcontainer/                # Dev container setup
│
├── .env.example                  # Environment variable template
├── requirements.txt              # Python dependencies
└── README.md
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| **LLM** | [Groq API](https://groq.com/) (`llama3`, `mixtral`, etc.) |
| **Embeddings** | HuggingFace `sentence-transformers` |
| **Vector DB** | [FAISS](https://faiss.ai/) (dense similarity search) |
| **Keyword Search** | BM25 via `rank_bm25` |
| **Reranker** | Cross-Encoder (`sentence-transformers`) |
| **RAG Framework** | [LangChain](https://www.langchain.com/) |
| **UI** | [Streamlit](https://streamlit.io/) |
| **PDF Parsing** | `pdfplumber` |
| **Image Handling** | `Pillow` |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- A free [Groq API key](https://console.groq.com/)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/prachiipahwa/codeRAG.git
cd codeRAG

# 2. Create and activate a virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Configure Environment

```bash
# Copy the example env file
cp .env.example .env

# Open .env and add your Groq API key
GROQ_API_KEY=your_groq_api_key_here
```

### Run the App

```bash
streamlit run app.py
```

The application will open at `http://localhost:8501`.

---

## 💡 Usage

### In the Streamlit UI

1. **Create a workspace** — Give your project a name
2. **Ingest a repository** — Paste a GitHub URL, upload a ZIP, or upload individual files
3. **Wait for indexing** — The system builds both vector and keyword indexes
4. **Start chatting** — Ask natural language questions about the codebase

### Example Questions

```
"Explain the overall architecture of this project."
"Where is user authentication implemented?"
"What does the DataIngestor class do?"
"Which modules interact with the database?"
"How does the retrieval pipeline work?"
"List all API endpoints."
```

### CLI Ingestion (Legacy)

For batch ingestion from the `data/` directory:

```bash
python ingest.py
```

This runs the full ingestion pipeline: loads files → chunks → builds FAISS index → builds BM25 index.

---

## 📊 Evaluation

CodeRAG ships with an evaluation module that measures retrieval quality against a ground-truth dataset.

```bash
python evaluate.py <workspace_name>
```

**Metrics computed:**

| Metric | Description |
|---|---|
| **Precision@K** | Fraction of retrieved docs at rank K that are relevant |
| **Recall@K** | Fraction of relevant docs found in top-K results |
| **MRR** | Mean Reciprocal Rank — how early the first relevant doc appears |

**Example output:**

```
Average Precision@3 : 0.400
Average Recall@3    : 1.200
Mean Reciprocal Rank: 0.400
```

To customize evaluation, edit `evaluation/eval_dataset.json`:

```json
[
  {
    "question": "Where is authentication handled?",
    "expected_sources": ["src/auth/handler.py"]
  }
]
```

---

## ☁️ Deployment (Streamlit Cloud)

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io) and create a new app
3. Select your fork and set `app.py` as the entry point
4. Under **Secrets**, add:
   ```
   GROQ_API_KEY = "your_groq_api_key_here"
   ```
5. Deploy — the live demo runs at [code-rag.streamlit.app](https://code-rag.streamlit.app/)

---

## 🤝 Contributing

Contributions are welcome! To get started:

1. Fork the repo and create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes and add tests if applicable
3. Run the app locally to verify: `streamlit run app.py`
4. Open a pull request with a clear description

**Areas where help is especially welcome:**
- Additional file type loaders (e.g., Jupyter notebooks, TypeScript)
- Improved chunking strategies for different languages
- Better evaluation datasets
- Dependency visualization features

---

## 🗺️ Roadmap

- [ ] Support for GitHub URL ingestion directly from the UI
- [ ] Repository dependency graph visualization
- [ ] Notebook (`.ipynb`) ingestion support
- [ ] Expanded evaluation dataset
- [ ] Improved multimodal diagram understanding
- [ ] Unit test coverage

---

## 👤 Author

**Prachi Pahwa**
