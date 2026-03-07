# CodeRAG (V2) – Developer Knowledge Assistant

CodeRAG V2 has been upgraded from a static RAG script into an interactive Developer Knowledge Assistant. 
It supports multiple isolated project workspaces, dynamic ingestion of Github Repos and Zip files, codebase structural mapping, caching, and a robust multiple-chat memory system.

## New Features (V2 Updates)
- **Dynamic Ingestion**: Clone GitHub repos or upload Zip archives directly via the UI.
- **Smart Hashing**: CodeRAG hashes files before embedding. Unchanged files are skipped during re-ingestion, saving massive API costs and time.
- **Codebase Mapping**: Generates a fast `repo_map.json` holding imports and functions for every file, creating a holistic representation of the repository inserted into the vector db.
- **Strict Quality Control RAG**: 
   - Multi-Query & HyDE generation via Groq.
   - Initial Wide retrieval (Top 20 via Dual FAISS + BM25 Ensemble).
   - Strict Filtering via `ms-marco-MiniLM-L-6-v2` Cross-Encoder scoring.
- **Workspaces & Memory**: SQLite-backed Chat sessions per project.

## Setup Instructions

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment:**
   Update or create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY="your-groq-api-key-here"
   ```

3. **Run the Application:**
   ```bash
   streamlit run app.py
   ```
   *Note: Ingestion is now handled entirely within the UI. Create a project workspace, and paste a Github link or upload files right from the browser.*

4. **Run Evaluation (Offline):**
   ```bash
   python evaluate.py <project_name>
   ```