import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.config import TAVILY_API_KEY, OPENROUTER_API_KEY
from src.providers.tavily_provider import TavilySearchProvider
from src.services.openrouter_service import OpenRouterAIService

def test_keys():
    print("--- 1. Testing Tavily Search API Key ---")
    tavily = TavilySearchProvider(TAVILY_API_KEY)
    print(f"Tavily Available: {tavily.is_available}")
    info = tavily.search_business_info("Toit Brewpub", "Bangalore")
    print(f"Tavily Search Result: {info}")

    print("\n--- 2. Testing OpenRouter Free LLM Key ---")
    ai = OpenRouterAIService(OPENROUTER_API_KEY)
    print(f"OpenRouter Available: {ai.is_available}")
    pitch = ai.generate_personalized_pitch(
        business_name="Koramangala Dental Care",
        category="Dental clinic",
        city="Bangalore",
        opportunity_type="No Official Website",
        suggested_service="Custom Responsive Website",
        agency_goal="Website Development"
    )
    print(f"OpenRouter AI Generated Pitch:\n{pitch}")

if __name__ == "__main__":
    test_keys()
