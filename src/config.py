import os
from dotenv import load_dotenv

# Load local environment if present
load_dotenv()

APP_NAME = "LeadFinder Free"
VERSION = "1.0.0"

# Nominatim Geocoding API
NOMINATIM_BASE_URL = os.getenv("NOMINATIM_BASE_URL", "https://nominatim.openstreetmap.org")
APP_USER_AGENT = os.getenv("APP_USER_AGENT", "LeadFinderFree/1.0 (contact: github-lead-finder)")

# Overpass API Public Endpoints (with fallback rotation)
OVERPASS_SERVERS = [
    os.getenv("OVERPASS_API_URL", "https://lz4.overpass-api.de/api/interpreter"),
    "https://overpass-api.de/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter"
]

# Request Timeouts & Limits
GEOCODE_TIMEOUT = 8
OVERPASS_TIMEOUT = 12
MAX_RESULTS_LIMIT = 200
DEFAULT_RESULTS_LIMIT = 50

# Google Maps via Serper API Key (2,500 free queries, no credit card required)
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "").strip()

# Optional Google Cloud Places Key (requires billing/credit card)
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "").strip()

# Tavily Search API Key
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "").strip()

# OpenRouter Free LLM API Key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()

# Recommended Free Models on OpenRouter
OPENROUTER_FREE_MODELS = [
    "google/gemini-2.0-flash-exp:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "qwen/qwen-2.5-coder-32b-instruct:free",
    "deepseek/deepseek-r1:free",
    "mistralai/mistral-7b-instruct:free"
]
OPENROUTER_DEFAULT_MODEL = "google/gemini-2.0-flash-exp:free"
