import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")

# Ensure base projects directory exists
os.makedirs(PROJECTS_DIR, exist_ok=True)

# API Keys and Models
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set. Please set it in your .env file.")

LLM_MODEL = "llama-3.3-70b-versatile"
VISION_MODEL = "llama-3.2-11b-vision-preview"
EMBEDDING_MODEL = "BAAI/bge-small-en"

# Retrieval & Ingestion Parameters
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
TOP_K_RETRIEVE = 20
TOP_K_COMPRESS = 5
SIMILARITY_THRESHOLD = 0.5 # Minimum Cross-Encoder score to retain a chunk

# UI Configuration
UI_THEME = {
    "background": "#0f172a",
    "sidebar": "#111827",
    "card": "#1f2937",
    "accent": "#6366f1",
    "text": "#e5e7eb",
    "border": "#374151"
}
