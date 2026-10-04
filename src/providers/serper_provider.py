import urllib.parse
import requests
from typing import List, Callable, Optional
from src.models import GeoBoundingBox, Lead
from src.providers.base import BusinessDataProvider
from src.services.normalizer import sanitize_phone, sanitize_url

class SerperGoogleMapsProvider(BusinessDataProvider):
    """
    Google Maps Lead Provider powered by Serper API (https://serper.dev).
    Features:
    - 2,500 FREE queries upon signup with ZERO credit card required.
    - Directly retrieves official Google Maps business listings, verified phone numbers,
      ratings, addresses, websites, and coordinates.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key.strip()
        self.base_url = "https://google.serper.dev/maps"

    @property
    def name(self) -> str:
        return "Google Maps (Serper API - 2,500 Free)"

    @property
    def is_free(self) -> bool:
        return True  # 2,500 free queries, no credit card required

    def search(
        self,
        bbox: GeoBoundingBox,
        category: str,
        keyword: Optional[str] = None,
        max_results: int = 50,
        progress_callback: Optional[Callable[[int, str], None]] = None,
        location_name: Optional[str] = None
    ) -> List[Lead]:
        if not self.api_key:
            raise ValueError(
                "Serper API Key is missing! "
                "Get 2,500 free searches at https://serper.dev (no credit card required) "
                "and paste your key in the sidebar or .env file."
            )

        # Construct natural language Google Maps search query
        # e.g., "Dental clinics in Koramangala, Bangalore, India"
        query_parts = [category]
        if keyword and keyword.strip():
            query_parts.append(keyword.strip())

        if location_name and location_name.strip():
            query_parts.append(f"in {location_name.strip()}")
        else:
            # Fallback using center coordinates
            center_lat = (bbox.north + bbox.south) / 2.0
            center_lon = (bbox.east + bbox.west) / 2.0
            query_parts.append(f"near {center_lat:.4f},{center_lon:.4f}")

        search_query = " ".join(query_parts)

        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }

        leads: List[Lead] = []
        page = 1
        max_pages = min(5, (max_results + 19) // 20)  # Serper returns 20 places per page

        while len(leads) < max_results and page <= max_pages:
            if progress_callback:
                progress_callback(
                    50 + (page * 5),
                    f"Querying Google Maps via Serper API (page {page})..."
                )

            payload = {
                "q": search_query,
                "page": page
            }

            try:
                response = requests.post(
                    self.base_url,
                    json=payload,
                    headers=headers,
                    timeout=15
                )

                if response.status_code == 403 or response.status_code == 401:
                    raise ValueError("Invalid Serper API Key or quota exhausted. Please check your key at https://serper.dev")

                if response.status_code != 200:
                    # Fallback to /places endpoint if /maps returned an error
                    fallback_url = "https://google.serper.dev/places"
                    response = requests.post(
                        fallback_url,
                        json=payload,
                        headers=headers,
                        timeout=15
                    )
                    if response.status_code != 200:
                        raise RuntimeError(f"Serper API error HTTP {response.status_code}: {response.text}")

                data = response.json()
                places = data.get("places", [])

                if not places:
                    break

                for p in places:
                    name = p.get("title", "").strip()
                    if not name:
                        continue

                    # Direct Google Maps phone number
                    raw_phone = p.get("phoneNumber", "")
                    phone = sanitize_phone(raw_phone)

                    # Website
                    raw_website = p.get("website", "")
                    website = sanitize_url(raw_website)

                    # Address
                    address = p.get("address", "").strip()

                    # Coordinates
                    lat = p.get("latitude")
                    lon = p.get("longitude")

                    # Maps link
                    cid = p.get("cid", "")
                    if cid:
                        maps_link = f"https://maps.google.com/?cid={cid}"
                    else:
                        encoded_query = urllib.parse.quote(f"{name} {address}".strip())
                        maps_link = f"https://www.google.com/maps/search/?api=1&query={encoded_query}"

                    place_cat = p.get("category", category)
                    rating = p.get("rating")
                    rating_count = p.get("ratingCount")

                    from src.services.normalizer import generate_whatsapp_link
                    wa_link = generate_whatsapp_link(phone, country=location_name or "")

                    lead = Lead(
                        business_name=name,
                        phone=phone,
                        whatsapp_link=wa_link,
                        address=address,
                        website=website,
                        maps_link=maps_link,
                        category=place_cat.title() if place_cat else category.title(),
                        source="Google Maps",
                        status="FOUND" if phone else "MISSING_PHONE",
                        lat=float(lat) if lat is not None else None,
                        lon=float(lon) if lon is not None else None,
                        raw_id=f"serper/{cid or name}",
                        tags={
                            "rating": rating,
                            "rating_count": rating_count,
                            "category": place_cat
                        }
                    )
                    leads.append(lead)

                    if len(leads) >= max_results:
                        break

                page += 1

            except ValueError:
                raise
            except Exception as e:
                # If network or parsing error occurred, stop pagination and return what we have
                break

        return leads
