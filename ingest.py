import sys
from src.ingestion.document_loaders import DataIngestor
from src.indexing.vector_store import VectorStoreManager
from src.indexing.sparse_store import SparseStoreManager

def main():
    print("--- Starting CodeRAG Data Ingestion Process ---")
    
    # 1. Ingest Data
    print("\nPhase 1: Loading and Chunking Files (Code, Docs, Diagrams)...")
    ingestor = DataIngestor()
    documents = ingestor.process_all()
    
    if not documents:
        print("No documents found in data/ directories.")
        sys.exit(1)
        
    print(f"Total chunks created: {len(documents)}")

    # 2. Build Vector Store
    print("\nPhase 2: Building FAISS Dense Index... (This might take a while)")
    vector_manager = VectorStoreManager()
    vector_manager.build_and_save(documents)

    # 3. Build Sparse Store
    print("\nPhase 3: Building BM25 Sparse Index...")
    sparse_manager = SparseStoreManager()
    sparse_manager.build_and_save(documents)
    
    print("\n--- Ingestion Complete! You can now run `streamlit run app.py` ---")

if __name__ == "__main__":
    main()
