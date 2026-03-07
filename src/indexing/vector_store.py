import os
from typing import List
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from src.config import EMBEDDING_MODEL, VECTOR_STORE_DIR

class VectorStoreManager:
    """Manages the dense vector embeddings using FAISS and HuggingFace sentence-transformers."""
    
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        self.index_name = "coderag_faiss"
        self.index_path = os.path.join(VECTOR_STORE_DIR, self.index_name)
        self.vector_store = None

    def build_and_save(self, documents: List[Document]):
        """Embeds documents into FAISS and saves to disk."""
        if not documents:
            print("No documents provided to build vector store.")
            return

        print(f"Building FAISS vector store with {len(documents)} chunks...")
        self.vector_store = FAISS.from_documents(documents, self.embeddings)
        self.vector_store.save_local(VECTOR_STORE_DIR, self.index_name)
        print("FAISS vector store saved successfully.")

    def load(self) -> FAISS:
        """Loads FAISS index from disk."""
        if os.path.exists(os.path.join(VECTOR_STORE_DIR, f"{self.index_name}.faiss")):
            print("Loading FAISS vector store...")
            self.vector_store = FAISS.load_local(
                VECTOR_STORE_DIR, 
                self.embeddings,
                index_name=self.index_name,
                allow_dangerous_deserialization=True # Required by LangChain to load local index
            )
            return self.vector_store
        else:
            raise FileNotFoundError("FAISS index not found. Please build it first.")
