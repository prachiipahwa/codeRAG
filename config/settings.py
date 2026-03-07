import os
from dotenv import load_dotenv

load_dotenv()

class Settings:

    # API Keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    # Embedding model
    EMBEDDING_MODEL = "BAAI/bge-small-en"

    # LLM model
    LLM_MODEL = "llama3-70b-8192"

    # Vector DB path
    VECTOR_DB_PATH = "vector_store"

    # Data directory
    DATA_PATH = "data"

    # Chunking parameters
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 100

    # Retrieval parameters
    TOP_K = 5