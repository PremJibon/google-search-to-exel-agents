import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tavily import TavilyClient
from src.config import TAVILY_API_KEY
from src.services.llm_helper import llm_helper

client = TavilyClient(api_key=TAVILY_API_KEY)
res = client.search(query="Gyms in Gulshan Dhaka phone address website", max_results=5)

raw_text = "\n\n".join([
    f"Title: {r.get('title')}\nURL: {r.get('url')}\nSnippet: {r.get('content')}"
    for r in res.get("results", [])
])

prompt = f"""From the search snippets below, extract real businesses in Gulshan Dhaka.
Return strictly a valid JSON array of objects with keys:
- "business_name": string
- "phone": string (or empty if not mentioned)
- "address": string (or empty if not mentioned)
- "website": string (official URL or social page URL, or empty)
- "category": "Gym"

Snippets:
{raw_text}

JSON:"""

response = llm_helper.call_llm([{"role": "user", "content": prompt}], temperature=0.1)
print("Groq Extraction Output:")
print(response)
