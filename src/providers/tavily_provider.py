from typing import List, Optional
from src.models import Lead

class TavilySearchProvider:
    """
    Search & enrichment provider using Tavily Search API.
    Used for web intelligence, finding missing business websites, and verifying online presence.
    Activated only when user inputs their Tavily API key.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key.strip()
        self.client = None
        if self.api_key:
            try:
                from tavily import TavilyClient
                self.client = TavilyClient(api_key=self.api_key)
            except Exception:
                self.client = None

    @property
    def is_available(self) -> bool:
        return self.client is not None

    def search_business_info(self, business_name: str, city: str) -> Optional[dict]:
        """
        Enriches a business by searching Tavily for official websites or active social media profiles.
        """
        if not self.is_available:
            return None

        try:
            query = f"{business_name} {city} official website contact"
            res = self.client.search(query=query, max_results=3)
            results = res.get("results", [])
            if results:
                top = results[0]
                return {
                    "url": top.get("url", ""),
                    "title": top.get("title", ""),
                    "snippet": top.get("content", "")
                }
        except Exception:
            pass

        return None
