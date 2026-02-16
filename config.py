"""
Configuration file for the Enterprise Policy Assistant
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Groq Configuration
GROQ_API_KEY = os.getenv("grok_api_key") or os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.1-8b-instant"  # Fast and efficient Llama model

# RAG Configuration
DOCS_FOLDER = "docs"
CHUNK_SIZE = 800  # Optimized for policy sections with headers
CHUNK_OVERLAP = 150  # Ensures context continuity
VECTOR_STORE_PATH = "vector_store"

# Embeddings Configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Agent Configuration
MAX_ITERATIONS = 5
TEMPERATURE = 0.1

# Streamlit Configuration
PAGE_TITLE = "Enterprise Policy Assistant"
PAGE_ICON = "🏢"

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables")

