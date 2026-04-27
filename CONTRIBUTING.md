# Contributing to CodeRAG

Thank you for your interest in contributing! This guide will help you get set up and explain how contributions are structured.

---

## Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/<your-username>/codeRAG.git
cd codeRAG
```

### 2. Set Up Your Environment

```bash
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
# Add your GROQ_API_KEY to .env
```

### 4. Run the App Locally

```bash
streamlit run app.py
```

---

## Project Layout for Contributors

The important directories for most contributions:

```
src/ingestion/       ← Add new file loaders here
src/indexing/        ← Modify indexing strategies here
src/retrieval/       ← Modify hybrid search / reranking here
src/generation/      ← Prompt templates and LLM wiring here
evaluation/          ← Add eval queries to eval_dataset.json
```

---

## How to Contribute

### Adding a New File Loader

1. Open `src/ingestion/document_loaders.py`
2. Add a new branch in `DataIngestor.process_all()` for your file extension
3. Return `List[Document]` objects with appropriate metadata
4. Test by placing sample files in `data/` and running `python ingest.py`

### Improving Retrieval

The retrieval pipeline lives in `src/retrieval/hybrid_search.py`. Common improvements:

- Adjusting top-K values per stage
- Swapping the reranker model
- Adding a new retrieval technique as an additional stage

### Adding Evaluation Queries

Edit `evaluation/eval_dataset.json` to add more ground-truth pairs:

```json
{
  "question": "Your test question",
  "expected_sources": ["path/to/expected/file.py"]
}
```

Run evaluation with:

```bash
python evaluate.py <workspace_name>
```

---

## Pull Request Guidelines

- Keep PRs focused on one change
- Include a short description of what changed and why
- Test the change locally before submitting
- If adding a feature, update the relevant section of `README.md` or `docs/ARCHITECTURE.md`

---

## Reporting Issues

Open a GitHub Issue with:
- A short description of the problem
- Steps to reproduce
- What you expected vs. what happened
- Python version and OS

---

## Code Style

- Follow PEP 8
- Use descriptive variable names
- Add a brief docstring to any new class or public method
