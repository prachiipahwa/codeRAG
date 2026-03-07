from typing import List
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.config import GROQ_API_KEY, LLM_MODEL

class QueryModifiers:
    """Handles query rewriting, multi-query generation, and HyDE."""
    
    def __init__(self):
        self.llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model=LLM_MODEL,
            temperature=0.0
        )

    def generate_multi_queries(self, original_query: str) -> List[str]:
        """Rewrites a single query into 3 distinct perspectives."""
        prompt = PromptTemplate(
            template="You are an AI language model assistant. Your task is to generate 3 "
            "different versions of the given user question to retrieve relevant documents from "
            "a vector database. By generating multiple perspectives on the user question, your "
            "goal is to help the user overcome some of the limitations of distance-based similarity "
            "search. Provide these alternative questions separated by newlines.\n\n"
            "Original question: {question}\n\n"
            "Alternative questions:\n",
            input_variables=["question"]
        )
        chain = prompt | self.llm | StrOutputParser()
        result = chain.invoke({"question": original_query})
        queries = [q.strip() for q in result.split("\n") if q.strip()]
        # Sometimes models number them
        queries = [q.lstrip("1234567890. -") for q in queries]
        return [original_query] + queries[:3]

    def generate_hyde_document(self, query: str) -> str:
        """Generates a hypothetical document based on the query for HyDE retrieval."""
        prompt = PromptTemplate(
            template="You are an expert developer. Please write a snippet of code, a documentation snippet, "
            "or an architectural explanation to answer the following question. "
            "Write the response strictly as if it was found in an internal codebase. "
            "Do not include conversational filler.\n\n"
            "Question: {question}\n\n"
            "Hypothetical snippet:",
            input_variables=["question"]
        )
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"question": query})
