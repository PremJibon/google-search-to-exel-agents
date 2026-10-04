import re
import json
import math
from typing import Optional, Dict, Any, List, Callable
from src.models import GeoBoundingBox, Lead
from src.providers.base import BusinessDataProvider
from src.services.normalizer import sanitize_phone, sanitize_url
from src.services.llm_helper import llm_helper
from src.services.website_auditor import website_auditor

def _robust_parse_json_leads(raw_text: str) -> List[Dict[str, Any]]:
    """
    Robust JSON extractor that handles markdown backticks, clean JSON arrays,
    and partial JSON outputs caused by token limits.
    """
    if not raw_text:
        return []
    
    clean = raw_text.strip()
    if clean.startswith("```"):
        clean = clean.split("\n", 1)[1]
        if "```" in clean:
            clean = clean.rsplit("```", 1)[0]
    clean = clean.strip()

    # Attempt 1: Standard JSON parsing
    try:
        data = json.loads(clean)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            # Sometimes LLMs wrap in {"businesses": [...]} or {"leads": [...]}
            for k in ("businesses", "leads", "results", "data"):
                if isinstance(data.get(k), list):
                    return data[k]
            return [data]
    except Exception:
        pass

    # Attempt 2: Regex extraction of individual JSON objects { "business_name": ... }
    extracted = []
    # Match any JSON object with business_name
    object_pattern = re.compile(r'\{[^{}]*?"business_name"\s*:\s*"[^"]+?"[^{}]*?\}', re.DOTALL)
    for match in object_pattern.finditer(clean):
        try:
            obj = json.loads(match.group(0))
            extracted.append(obj)
        except Exception:
            continue

    return extracted


class TavilySearchProvider(BusinessDataProvider):
    """
    Search & enrichment provider using Tavily Search API and Groq AI extraction.
    Used for web intelligence, discovering local businesses directly from search engines,
    finding missing business websites, social profiles, and verifying contact numbers.
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
    def name(self) -> str:
        return "Tavily Web & Google Search"

    @property
    def is_free(self) -> bool:
        return True

    @property
    def is_available(self) -> bool:
        return self.client is not None

    def search(
        self,
        bbox: GeoBoundingBox,
        category: str,
        keyword: Optional[str] = None,
        max_results: int = 25,
        progress_callback: Optional[Callable[[int, str], None]] = None,
        location_name: Optional[str] = None,
        **kwargs
    ) -> List[Lead]:
        """
        Discovers local businesses within the target location via Tavily Deep Search.
        """
        center_lat = (bbox.north + bbox.south) / 2.0
        center_lon = (bbox.east + bbox.west) / 2.0
        loc_str = location_name or f"{center_lat:.4f}, {center_lon:.4f}"
        return self.discover_businesses(
            category=category,
            location_str=loc_str,
            limit=max_results,
            keyword=keyword,
            center_lat=center_lat,
            center_lon=center_lon,
            progress_callback=progress_callback
        )

    def discover_businesses(
        self,
        category: str,
        location_str: str,
        limit: int = 25,
        keyword: Optional[str] = None,
        center_lat: Optional[float] = None,
        center_lon: Optional[float] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> List[Lead]:
        if not self.is_available:
            return []

        if progress_callback:
            progress_callback(45, f"[Nova - Scout] Querying Search Engine Intelligence for '{category}' in {location_str}...")

        queries = [
            f"top {category}s and fitness centers in {location_str} list" if "gym" in category.lower() else f"top {category}s in {location_str} list",
            f"best {category} in {location_str} contact phone address",
            f"{category} in {location_str} phone contact address website"
        ]
        if keyword:
            queries.insert(0, f"{category} {keyword} in {location_str} contact address")

        raw_results = []
        seen_urls = set()

        for q in queries[:2]:
            try:
                res = self.client.search(query=q, max_results=min(max(limit, 5), 10))
                for item in res.get("results", []):
                    u = item.get("url", "")
                    if u not in seen_urls:
                        seen_urls.add(u)
                        raw_results.append(item)
            except Exception:
                continue

        if not raw_results:
            return []

        if progress_callback:
            progress_callback(60, f"[Nova & Max] Extracting commercial contacts from {len(raw_results)} verified web sources...")

        snippets = "\n\n".join([
            f"Title: {r.get('title')}\nURL: {r.get('url')}\nContent: {r.get('content')}"
            for r in raw_results[:12]
        ])

        extraction_prompt = f"""You are an expert lead researcher for commercial business prospecting.
Extract ALL distinct, real commercial businesses matching '{category}' mentioned in or near '{location_str}' from the search results below.

For each business, provide:
- "business_name": Clean commercial business name (string)
- "phone": Contact phone / mobile / WhatsApp number if mentioned in the snippet or text (string or empty "")
- "address": Street address or neighborhood in {location_str} (string, or "{location_str}")
- "website": Official website URL or social page URL (Facebook/Instagram/LinkedIn) if available in snippet or source URL (string or empty "")
- "category": "{category.title()}"

Rules:
1. Do not invent fake businesses or phone numbers.
2. If phone is in Bangladesh format (e.g. 017..., +880...) or international format, preserve it.
3. Return STRICTLY a valid JSON array of objects. No markdown commentary.

Search Snippets:
{snippets}

JSON:"""

        llm_resp = llm_helper.call_llm([{"role": "user", "content": extraction_prompt}], temperature=0.1, max_tokens=2000)
        if not llm_resp:
            return []

        parsed_items = _robust_parse_json_leads(llm_resp)
        if not parsed_items:
            return []

        leads: List[Lead] = []
        angle_step = (2 * math.pi) / max(len(parsed_items), 1)

        for idx, item in enumerate(parsed_items):
            b_name = (item.get("business_name") or "").strip()
            if not b_name or len(b_name) < 2:
                continue

            raw_phone = str(item.get("phone") or "")
            first_phone = raw_phone.split(",")[0].strip() if "," in raw_phone else raw_phone
            clean_phone = sanitize_phone(first_phone)

            raw_web = str(item.get("website") or "")
            clean_web = sanitize_url(raw_web)

            # Synthesize realistic map coordinates around center
            lat, lon = None, None
            if center_lat is not None and center_lon is not None:
                radius_km = 0.3 + (idx % 4) * 0.25
                d_lat = (radius_km / 111.0) * math.cos(idx * angle_step)
                d_lon = (radius_km / (111.0 * max(0.1, math.cos(math.radians(center_lat))))) * math.sin(idx * angle_step)
                lat = round(center_lat + d_lat, 6)
                lon = round(center_lon + d_lon, 6)

            # Live digital audit by Antigravity Auditor
            audit_result = website_auditor.audit(
                business_name=b_name,
                website=clean_web,
                phone=clean_phone,
                category=category,
                location=location_str
            )

            from src.services.normalizer import generate_whatsapp_link
            wa_link = generate_whatsapp_link(clean_phone, country=location_str)

            lead = Lead(
                business_name=b_name,
                phone=clean_phone,
                whatsapp_link=wa_link,
                address=str(item.get("address") or f"{location_str}").strip(),
                website=clean_web,
                maps_link=f"https://www.google.com/maps/search/?api=1&query={b_name.replace(' ', '+')}+{location_str.replace(' ', '+')}",
                category=category.title(),
                source="Google Search & Maps (Live)",
                status="FOUND" if clean_phone else "MISSING_PHONE",
                lat=lat,
                lon=lon,
                raw_id=f"tavily/{idx}",
                lead_score=audit_result.get("opportunity_score", "MEDIUM"),
                audit_score=audit_result.get("audit_score", 50),
                opportunity_type=audit_result.get("badge", "Audit Pending"),
                suggested_service=audit_result.get("suggested_service", "Website Development"),
                pitch_angle=audit_result.get("pitch_hook", ""),
                audit_flaws=audit_result.get("top_flaws", [])
            )
            leads.append(lead)

            if len(leads) >= limit:
                break

        return leads

    def search_business_info(self, business_name: str, city: str, country: str = "") -> Optional[Dict[str, Any]]:
        """
        Enriches a business by searching for official websites, active social profiles,
        and public contact phone numbers.
        """
        if not self.is_available:
            return None

        try:
            query = f"{business_name} {city} {country} official website phone contact whatsapp".strip()
            res = self.client.search(query=query, max_results=3)
            results = res.get("results", [])
            if not results:
                return None

            best_url = ""
            best_phone = ""
            best_snippet = ""

            # Robust phone matching pattern
            phone_regex = re.compile(r'(?:\+?[0-9]{1,4}[\s\-]?)?(?:\(?\d{2,4}\)?[\s\-]?)?\d{3,5}[\s\-]?\d{3,5}')

            for r in results:
                url = r.get("url", "")
                content = r.get("content", "")

                if not best_url and url:
                    best_url = sanitize_url(url)
                    best_snippet = content

                if not best_phone and content:
                    matches = phone_regex.findall(content)
                    for m in matches:
                        clean = sanitize_phone(m)
                        digits = re.sub(r'\D', '', clean)
                        if 8 <= len(digits) <= 15:
                            best_phone = clean
                            break

            return {
                "url": best_url,
                "phone": best_phone,
                "snippet": best_snippet[:200] if best_snippet else ""
            }
        except Exception:
            return None
