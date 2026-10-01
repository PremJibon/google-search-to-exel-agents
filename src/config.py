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
    os.getenv("OVERPASS_API_URL", "https://overpass-api.de/api/interpreter"),
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter"
]

# Request Timeouts & Limits
GEOCODE_TIMEOUT = 10
OVERPASS_TIMEOUT = 30
MAX_RESULTS_LIMIT = 200
DEFAULT_RESULTS_LIMIT = 50

# Optional Google Places Key
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "").strip()
