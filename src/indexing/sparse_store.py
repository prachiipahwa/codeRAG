import os
import pickle
from typing import List
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from src.config import VECTOR_STORE_DIR

class SparseStoreManager:
    """Manages the sparse keyword index using BM25."""
    
    def __init__(self):
        self.index_path = os.path.join(VECTOR_STORE_DIR, "bm25_index.pkl")
        self.retriever = None

    def build_and_save(self, documents: List[Document]):
        """Builds BM25 index from documents and saves to disk via pickle."""
        if not documents:
            print("No documents provided to build BM25 store.")
            return

        print(f"Building BM25 sparse index with {len(documents)} chunks...")
        self.retriever = BM25Retriever.from_documents(documents)
        
        # Save exact matches structure
        with open(self.index_path, "wb") as f:
            pickle.dump(self.retriever, f)
        print("BM25 index saved successfully.")

    def load(self) -> BM25Retriever:
        """Loads BM25 index from disk."""
        if os.path.exists(self.index_path):
            print("Loading BM25 store...")
            with open(self.index_path, "rb") as f:
                self.retriever = pickle.load(f)
            return self.retriever
        else:
            raise FileNotFoundError("BM25 index not found. Please build it first.")
