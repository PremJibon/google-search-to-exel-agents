import requests
from src.config import TAVILY_API_KEY, OPENROUTER_API_KEY

print("--- Testing Tavily directly ---")
try:
    from tavily import TavilyClient
    client = TavilyClient(api_key=TAVILY_API_KEY)
    res = client.search(query="restaurants in Bangalore", max_results=2)
    print("Tavily response keys:", res.keys())
    print("Tavily results count:", len(res.get("results", [])))
    if res.get("results"):
        print("First result title:", res["results"][0].get("title"))
except Exception as e:
    print("Tavily error:", type(e), e)

print("\n--- Testing OpenRouter directly ---")
try:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "LeadFinder",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "meta-llama/llama-3.3-70b-instruct:free",
        "messages": [{"role": "user", "content": "Say hello in one word."}]
    }
    resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=10)
    print("OpenRouter status:", resp.status_code)
    print("OpenRouter body:", resp.text)
except Exception as e:
    print("OpenRouter error:", type(e), e)
