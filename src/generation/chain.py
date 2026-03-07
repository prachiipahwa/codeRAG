from typing import List, Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from src.config import GROQ_API_KEY, LLM_MODEL

class RAGChain:
    """Handles the final generation using Groq LLM grounded in retrieved context."""

    def __init__(self):
        self.llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model=LLM_MODEL,
            temperature=0.2, # Slight creativity for explanation, but mostly factual
            max_tokens=2048
        )
        self.prompt = self._create_prompt()

    def _create_prompt(self):
        """Creates the chat prompt with citation instructions."""
        system_template = """You are an expert developer and AI assistant named CodeRAG, designed to help engineers understand their software codebase.
You have been provided with contextual snippets from the codebase, documentation, and architecture diagrams.

Instructions:
1. Answer the user's question clearly and comprehensively using ONLY the provided context.
2. If the answer is not contained within the context, state that you do not have enough information rather than hallucinating.
3. CRITICAL: You MUST include inline source citations using the metadata provided in the context. Format your citations like `[filename.ext]`.
4. If providing code, explain it briefly but concisely.

Context:
{context}"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_template),
            MessagesPlaceholder(variable_name="chat_history"), # For conversational memory
            ("human", "{question}")
        ])
        return prompt

    def format_docs(self, docs) -> str:
        """Formats the Langchain Documents into a single context string with metadata."""
        formatted = []
        for i, doc in enumerate(docs):
            source = doc.metadata.get("source", "Unknown Source")
            doc_type = doc.metadata.get("type", "Unknown Type")
            formatted.append(f"--- Document {i+1} : {source} ({doc_type}) ---\n{doc.page_content}\n")
        return "\n".join(formatted)

    def generate(self, question: str, retrieved_docs: List[Any], chat_history: List[Dict[str, Any]] = None) -> str:
        """Invokes the Chain to generate an answer, utilizing previous chat memory."""
        context_str = self.format_docs(retrieved_docs)
        
        # Format the SQLite dicts into LangChain history tuples
        formatted_history = []
        if chat_history:
            for msg in chat_history:
                if msg["role"] == "user":
                    formatted_history.append(("human", msg["content"]))
                elif msg["role"] == "assistant":
                    formatted_history.append(("assistant", msg["content"]))
                    
        chain = self.prompt | self.llm | StrOutputParser()
        return chain.invoke({
            "context": context_str,
            "chat_history": formatted_history,
            "question": question
        })
