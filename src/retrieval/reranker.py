from typing import List
from langchain_core.documents import Document
from sentence_transformers import CrossEncoder

class Reranker:
    """Handles contextual compression and reranking of retrieved documents."""
    
    def __init__(self):
        # Extremely fast and effective cross-encoder map for routing query, doc pairs
        self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    def rerank_and_compress(self, query: str, documents: List[Document], top_k: int = 5) -> List[Document]:
        """Reranks retrieved documents via a CrossEncoder and trims to top_k to compress context."""
        if not documents:
            return []

        # Form (query, document) pairs
        pairs = [[query, doc.page_content] for doc in documents]
        
        # Predict relevancy scores
        scores = self.cross_encoder.predict(pairs)
        
        # Add scores to documents and sort
        doc_score_pairs = list(zip(documents, scores))
        
        # Sort by score descending
        doc_score_pairs.sort(key=lambda x: x[1], reverse=True)
        
        # Extract the top_k documents
        reranked_docs = [doc for doc, _ in doc_score_pairs[:top_k]]
        
        # Context Compression step: In a full pipeline, we could use an LLM Context Compressor.
        # But keeping only top_k highly relevant documents after CrossEncoder reduces token usage.
        return reranked_docs
