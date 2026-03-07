from typing import List
from langchain_core.documents import Document

class StandardMetrics:
    """Calculates Precision, Recall, and MRR for retrieval evaluation."""

    @staticmethod
    def calculate_precision_at_k(retrieved_docs: List[Document], expected_sources: List[str], k: int) -> float:
        """Precision@k = (Relevant docs in top k) / k"""
        if not retrieved_docs or k <= 0:
            return 0.0
            
        top_k_docs = retrieved_docs[:k]
        relevant_count = 0
        for doc in top_k_docs:
            source = doc.metadata.get("source", "")
            if any(exp in source for exp in expected_sources):
                relevant_count += 1
                
        return relevant_count / k

    @staticmethod
    def calculate_recall_at_k(retrieved_docs: List[Document], expected_sources: List[str], k: int) -> float:
        """Recall@k = (Relevant docs in top k) / Total relevant expected docs"""
        if not expected_sources or not retrieved_docs or k <= 0:
            return 0.0
            
        top_k_docs = retrieved_docs[:k]
        relevant_count = 0
        for doc in top_k_docs:
            source = doc.metadata.get("source", "")
            if any(exp in source for exp in expected_sources):
                relevant_count += 1
                
        # In a real system you might have a known # of total relevant chunks
        # Here we normalize against the unique expected source files
        return relevant_count / len(expected_sources)

    @staticmethod
    def calculate_mrr(retrieved_docs: List[Document], expected_sources: List[str]) -> float:
        """Mean Reciprocal Rank (MRR) = 1/rank of first relevant document."""
        for rank, doc in enumerate(retrieved_docs, start=1):
            source = doc.metadata.get("source", "")
            if any(exp in source for exp in expected_sources):
                return 1.0 / rank
        return 0.0
