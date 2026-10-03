import os
from dotenv import load_dotenv

# Load local environment if present
load_dotenv()

APP_NAME = "LeadFinder Free"
VERSION = "2.1.0"

def get_secret(key: str, default: str = "") -> str:
    """
    Safely retrieves a configuration key across environments:
    1. OS Environment variable (.env or Render)
    2. Streamlit Community Cloud (st.secrets)
    3. Default fallback
    """
    val = os.getenv(key)
    if val is not None and str(val).strip():
        return str(val).strip()
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            return str(st.secrets[key]).strip()
    except Exception:
        pass
    return default

# Nominatim Geocoding API
NOMINATIM_BASE_URL = get_secret("NOMINATIM_BASE_URL", "https://nominatim.openstreetmap.org")
APP_USER_AGENT = get_secret("APP_USER_AGENT", "LeadFinderFree/2.1 (contact: github-lead-finder)")

# Overpass API Public Endpoints (with reliable fallback rotation)
OVERPASS_SERVERS = [
    get_secret("OVERPASS_API_URL", "https://overpass-api.de/api/interpreter"),
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter"
]

# Request Timeouts & Limits
GEOCODE_TIMEOUT = 8
OVERPASS_TIMEOUT = 4.5
MAX_RESULTS_LIMIT = 200
DEFAULT_RESULTS_LIMIT = 50

# ========================================================
# ⚡ PRIMARY AI ENGINE: Groq (Ultra-Fast LPU Inference)
# ========================================================
GROQ_API_KEY = get_secret("GROQ_API_KEY", "")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODELS = [
    "openai/gpt-oss-120b",
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-20b"
]
GROQ_DEFAULT_MODEL = "openai/gpt-oss-120b"

# Google Maps via Serper API Key (Free tier 2,500 queries at https://serper.dev)
SERPER_API_KEY = get_secret("SERPER_API_KEY", "")

# Optional Google Cloud Places Key (Maps JS API & Places)
GOOGLE_MAPS_API_KEY = get_secret("GOOGLE_MAPS_API_KEY", "")

# Tavily Search API Key (Enrichment and deep intelligence)
TAVILY_API_KEY = get_secret("TAVILY_API_KEY", "")

# OpenRouter LLM API Key (Secondary / Multi-Model Fallback)
OPENROUTER_API_KEY = get_secret("OPENROUTER_API_KEY", "")
OPENROUTER_FREE_MODELS = [
    "qwen/qwen3.8-27b:free",
    "liquid/lfm-2.5-2.6b:free",
    "nvidia/nemotron-3.5-lightning:free",
    "google/gemini-2.0-flash-001"
]
OPENROUTER_DEFAULT_MODEL = "qwen/qwen3.8-27b:free"

# BazaarLink AI Helper (OpenAI-compatible assistant at https://api.bazaarlink.ai/v1)
BAZAARLINK_BASE_URL = get_secret("BAZAARLINK_BASE_URL", "https://api.bazaarlink.ai/v1")
BAZAARLINK_API_KEY = get_secret("BAZAARLINK_API_KEY", "")
