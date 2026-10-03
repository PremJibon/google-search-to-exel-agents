import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tavily import TavilyClient
from src.config import TAVILY_API_KEY
from src.services.llm_helper import llm_helper
from src.services.normalizer import sanitize_phone, sanitize_url
from src.models import Lead

def tavily_discover(category: str, location_str: str, limit: int = 10, center_lat: float = 23.792, center_lon: float = 90.415):
    client = TavilyClient(api_key=TAVILY_API_KEY)
    queries = [
        f"{category}s in {location_str} phone address website",
        f"best {category} {location_str} contact number"
    ]
    raw_results = []
    seen_urls = set()
    for q in queries:
        try:
            res = client.search(query=q, max_results=5)
            for r in res.get("results", []):
                u = r.get("url", "")
                if u not in seen_urls:
                    seen_urls.add(u)
                    raw_results.append(r)
        except Exception as e:
            print("Query err:", e)

    print(f"Total raw results fetched: {len(raw_results)}")
    snippets = "\n\n".join([
        f"Title: {r.get('title')}\nURL: {r.get('url')}\nContent: {r.get('content')}"
        for r in raw_results
    ])

    prompt = f"""You are an elite data extraction AI.
Extract distinct, real commercial businesses matching the niche '{category}' in or near '{location_str}' from these search results.

For each business, extract:
- "business_name": clean business name
- "phone": contact phone or mobile number (or "" if missing)
- "address": street address / area (or "" if missing)
- "website": official website URL or social page URL (or "" if missing)
- "category": "{category}"

Return strictly a JSON array of objects.

Search Results:
{snippets}

JSON:"""

    resp = llm_helper.call_llm([{"role": "user", "content": prompt}], temperature=0.1)
    clean = resp.strip()
    if clean.startswith("```"):
        clean = clean.split("\n", 1)[1].rsplit("```", 1)[0]
    
    parsed = json.loads(clean.strip())
    print(f"Extracted {len(parsed)} businesses:")
    for b in parsed:
        print(f"- {b['business_name']} | Phone: {b['phone']} | Web: {b['website']} | Addr: {b['address']}")

if __name__ == "__main__":
    tavily_discover("Gym", "Gulshan, Dhaka", limit=5)
