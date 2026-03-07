import os
import pickle
from typing import List, Tuple
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain_huggingface import HuggingFaceEmbeddings
from src.config import EMBEDDING_MODEL
from src.workspace_manager import WorkspaceManager
from src.logger import logger

class IndexManager:
    """Manages project-scoped Vector (FAISS) and Sparse (BM25) indexes."""

    def __init__(self, project_name: str):
        self.dirs = WorkspaceManager.get_project_dirs(project_name)
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        self.index_name = "faiss_index"
        
    def build_and_save(self, documents: List[Document]):
        """Builds both FAISS and BM25 and persists them into the project workspace."""
        if not documents:
            logger.warning("No documents provided to build indexes.")
            return

        logger.info(f"Building FAISS vector store with {len(documents)} chunks...")
        vector_store = FAISS.from_documents(documents, self.embeddings)
        vector_store.save_local(self.dirs["vector_store"], self.index_name)
        
        logger.info(f"Building BM25 sparse index with {len(documents)} chunks...")
        bm25_retriever = BM25Retriever.from_documents(documents)
        with open(self.dirs["bm25_index"], "wb") as f:
            pickle.dump(bm25_retriever, f)
            
        logger.info(f"Successfully saved both indexes to {self.dirs['base']}")

    def load_indexes(self) -> Tuple[FAISS, BM25Retriever]:
        """Loads and returns both indexes. Raises FileNotFoundError if missing."""
        if not os.path.exists(os.path.join(self.dirs["vector_store"], f"{self.index_name}.faiss")):
            raise FileNotFoundError(f"FAISS index not found for project in {self.dirs['vector_store']}")
            
        if not os.path.exists(self.dirs["bm25_index"]):
            raise FileNotFoundError(f"BM25 index not found for project at {self.dirs['bm25_index']}")
            
        vector_store = FAISS.load_local(
            self.dirs["vector_store"], 
            self.embeddings,
            index_name=self.index_name,
            allow_dangerous_deserialization=True
        )
        
        with open(self.dirs["bm25_index"], "rb") as f:
            bm25_retriever = pickle.load(f)
            
        return vector_store, bm25_retriever
