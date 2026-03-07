from typing import List, Dict, Any, Tuple
from langchain_core.documents import Document
from langchain_classic.retrievers import EnsembleRetriever
from src.retrieval.query_modifiers import QueryModifiers
from src.retrieval.reranker import Reranker
from src.indexing.index_manager import IndexManager
from src.config import TOP_K_RETRIEVE, TOP_K_COMPRESS, SIMILARITY_THRESHOLD
from src.logger import logger

class HybridRetriever:
    """Dynamic hybrid retriever supporting thresholds, project scoping, and debugging."""
    
    def __init__(self, project_name: str):
        self.index_manager = IndexManager(project_name)
        self.faiss_store, self.bm25_retriever = self.index_manager.load_indexes()
        
        # Pull 15 chunks from Vector, 15 from BM25 before Reciprocal Rank Fusion
        self.faiss_retriever = self.faiss_store.as_retriever(search_kwargs={"k": 15})
        self.bm25_retriever.k = 15 
        
        self.ensemble_retriever = EnsembleRetriever(
            retrievers=[self.faiss_retriever, self.bm25_retriever],
            weights=[0.5, 0.5]
        )
        
        self.query_modifiers = QueryModifiers()
        self.reranker = Reranker()
        
        # Store debug info for current run
        self.debug_info = {}

    def retrieve(self, query: str) -> Tuple[List[Document], Dict[str, Any]]:
        """Retrieves and deeply filters chunks, returning the final docs and debug traces."""
        
        logger.info(f"Starting advanced retrieval for: '{query}'")
        self.debug_info = {"original_query": query}
        
        # 1. Multi-Query Expansion
        expanded_queries = self.query_modifiers.generate_multi_queries(query)
        self.debug_info["multi_queries"] = expanded_queries[1:] # Exclude the original included at pos 0
        
        # 2. HyDE document generation
        hyde_doc = self.query_modifiers.generate_hyde_document(query)
        self.debug_info["hyde_document"] = hyde_doc
        expanded_queries.append(hyde_doc)
        
        # 3. Ensemble Retrieval across all query variants
        all_retrieved_docs = []
        for q in expanded_queries:
            docs = self.ensemble_retriever.invoke(q)
            all_retrieved_docs.extend(docs)
            
        unique_docs = self._deduplicate(all_retrieved_docs)
        
        # Take the top TOP_K_RETRIEVE highest frequency/scored docs from RRF ensemble
        candidate_docs = unique_docs[:TOP_K_RETRIEVE]
        
        # 4. Cross Encoder Reranking
        scored_docs = self._rerank_with_scores(query, candidate_docs)
        self.debug_info["reranked_scores"] = [
            {"source": doc.metadata.get("source"), "score": score, "content": doc.page_content[:100] + "..."} 
            for doc, score in scored_docs
        ]
        
        # 5. Context Compression & Similarity Threshold Filtering
        final_docs = []
        for doc, score in scored_docs:
            if score >= SIMILARITY_THRESHOLD:
                final_docs.append(doc)
            if len(final_docs) >= TOP_K_COMPRESS:
                break
                
        # Fallback if strict threshold dropped everything, keep top 1 just in case
        if not final_docs and scored_docs:
            final_docs = [scored_docs[0][0]]
            
        logger.info(f"Retrieval complete. Filtered down to {len(final_docs)} chunks from {len(candidate_docs)} candidates.")
        return final_docs, self.debug_info

    def _rerank_with_scores(self, query: str, documents: List[Document]) -> List[Tuple[Document, float]]:
        """Reranks and returns raw paired scores for debugging."""
        if not documents:
            return []
        pairs = [[query, doc.page_content] for doc in documents]
        scores = self.reranker.cross_encoder.predict(pairs)
        doc_score_pairs = list(zip(documents, scores))
        doc_score_pairs.sort(key=lambda x: x[1], reverse=True)
        return doc_score_pairs

    def _deduplicate(self, documents: List[Document]) -> List[Document]:
        """Remove duplicates preserving order."""
        seen = set()
        unique = []
        for doc in documents:
            if doc.page_content not in seen:
                seen.add(doc.page_content)
                unique.append(doc)
        return unique
