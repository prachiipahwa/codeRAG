# CodeRAG – Developer Knowledge Assistant

CodeRAG is an **Advanced Retrieval-Augmented Generation (RAG) system** designed to help developers understand large codebases quickly.
It allows users to **ingest GitHub repositories, documentation, and diagrams**, then ask natural language questions about the project.

The system retrieves relevant code snippets and documents using a hybrid search pipeline and generates contextual explanations using a large language model.

---

## Key Features

### Developer-Focused RAG System

* Query software repositories using natural language
* Retrieve relevant code snippets and documentation
* Explain repository structure and architecture

### Advanced Retrieval Pipeline

CodeRAG implements several modern RAG techniques:

* Hybrid Retrieval (**FAISS + BM25**)
* Multi-Query Retrieval
* HYDE (Hypothetical Document Embedding)
* Cross-Encoder Reranking
* Context Compression
* Source Citation

### Dynamic Repository Ingestion

Users can ingest repositories dynamically by:

* Providing a GitHub repository URL
* Uploading a ZIP archive
* Uploading individual files

The system automatically:

* scans repository files
* chunks documents
* generates embeddings
* builds vector and keyword indexes

### Workspace Management

Each project runs inside an isolated workspace containing:

* FAISS vector index
* BM25 keyword index
* repository metadata
* chat session history

This allows users to work with multiple repositories independently.

### Conversational Interface

CodeRAG provides a chat interface where developers can:

* explore codebases
* understand architecture
* locate functions and modules
* inspect retrieved source documents

---

## System Architecture

The system consists of four main components.

### Data Ingestion

Loads repository files and documentation and prepares them for indexing.

Supported sources:

* Code files
* Markdown / documentation
* PDFs
* Architecture diagrams

### Indexing

Documents are processed using:

* HuggingFace embeddings
* FAISS vector database
* BM25 keyword search

### Retrieval Pipeline

The retrieval process includes:

1. Query rewriting
2. Multi-query generation
3. HYDE document generation
4. Hybrid retrieval (FAISS + BM25)
5. Cross-encoder reranking
6. Context filtering

### Generation

The final response is generated using **Groq LLMs**, with retrieved context included in the prompt.

---

## Project Structure

```
codeRAG
│
├── app.py
├── src/
│   ├── ingestion/
│   ├── indexing/
│   ├── retrieval/
│   ├── generation/
│   ├── workspace_manager.py
│   └── chat_manager.py
│
├── evaluation/
│   ├── eval_dataset.json
│   └── evaluate.py
│
├── projects/
│   └── (generated workspaces)
│
├── requirements.txt
└── README.md
```

---

## Technologies Used

* **LangChain** – RAG orchestration
* **HuggingFace Transformers** – embeddings and reranking
* **FAISS** – vector similarity search
* **BM25** – keyword retrieval
* **Groq API** – LLM inference
* **Streamlit** – user interface
* **GitPython** – repository ingestion

---

## Installation

Clone the repository.

```bash
git clone https://github.com/prachiipahwa/codeRAG.git
cd codeRAG
```

Create a virtual environment.

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file and add your Groq API key.

```
GROQ_API_KEY=your_api_key_here
```

---

## Running the Application

Start the Streamlit interface.

```bash
streamlit run app.py
```

The application will open in your browser.

---

## Using the System

1. Create a workspace
2. Ingest a repository (GitHub URL or files)
3. Wait for indexing to complete
4. Start a chat session
5. Ask questions about the repository

Example questions:

* Explain the architecture of this repository
* Where is authentication implemented?
* Which modules interact with the database?
* Summarize the project structure

---

## Evaluation

The system includes an evaluation module that measures retrieval quality using:

* Precision@K
* Recall@K
* Mean Reciprocal Rank (MRR)

Run evaluation with:

```bash
python evaluate.py <workspace_name>
```

Example output:

```
Average Precision@3 : 0.40
Average Recall@3    : 1.20
Mean Reciprocal Rank: 0.40
```

---

## Deployment

The application can be deployed easily using **Streamlit Cloud**.

Steps:

1. Push the repository to GitHub
2. Create a new Streamlit Cloud app
3. Select `app.py` as the entry point
4. Add `GROQ_API_KEY` to Secrets

---

## Example Use Case

Developers often struggle to understand unfamiliar repositories quickly.
CodeRAG allows them to ingest a repository and ask questions such as:

* “Explain the architecture of this project.”
* “Where is the main agent logic implemented?”
* “How does the system process user inputs?”

The assistant retrieves relevant code snippets and provides explanations grounded in the repository context.

---

## Future Improvements

Potential enhancements include:

* improved UI/UX layout
* repository dependency visualization
* better evaluation datasets
* additional multimodal support

---

## Author

Prachi Pahwa

---
