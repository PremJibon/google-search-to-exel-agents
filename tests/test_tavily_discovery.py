import sys
import os
import json
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tavily import TavilyClient
from src.config import TAVILY_API_KEY
from src.models import GeoBoundingBox, Lead
from src.services.llm_helper import llm_helper
from src.services.normalizer import sanitize_phone, sanitize_url

def test_tavily_discovery(category="Gym", location="Gulshan, Dhaka, Bangladesh", limit=10):
    client = TavilyClient(api_key=TAVILY_API_KEY)
    query = f"{category} in {location} phone contact address website"
    print(f"Searching Tavily: {query}")
    res = client.search(query=query, max_results=max(limit, 5))
    results = res.get("results", [])
    print(f"Found {len(results)} raw search results")

    snippets = []
    for r in results:
        snippets.append(f"Title: {r.get('title')}\nURL: {r.get('url')}\nContent: {r.get('content')}")
    combined = "\n\n---\n\n".join(snippets)

    extraction_prompt = f"""You are an elite data extraction assistant.
Extract all real commercial businesses matching '{category}' in or around '{location}' from the search snippets below.

For each business, extract:
- "business_name": Clean business name (string)
- "phone": Contact phone or mobile or WhatsApp number if found in snippet (string or empty "")
- "address": Physical address or street if mentioned (string or empty "")
- "website": Official website URL or social page URL (Facebook/Instagram) if found (string or empty "")
- "category": "{category}"

Return strictly a valid JSON array of objects. Do not invent any data. If not mentioned, leave empty "".

Search Snippets:
{combined}

JSON Array:"""

    resp = llm_helper.call_llm([{"role": "user", "content": extraction_prompt}], temperature=0.1)
    # Parse json
    try:
        # strip markdown code blocks if any
        clean_json = resp.strip()
        if clean_json.startswith("```"):
            clean_json = clean_json.split("\n", 1)[1]
            if clean_json.endswith("```"):
                clean_json = clean_json.rsplit("```", 1)[0]
        parsed = json.loads(clean_json.strip())
        print(f"Successfully extracted {len(parsed)} businesses:")
        for item in parsed:
            print("Business:", item.get("business_name"))
            print("  Phone:", item.get("phone"))
            print("  Web:", item.get("website"))
            print("  Addr:", item.get("address"))
    except Exception as e:
        print("JSON parse error:", e)
        print("Raw response:", resp)

if __name__ == "__main__":
    test_tavily_discovery("Gym", "Gulshan, Dhaka, Bangladesh", 5)
