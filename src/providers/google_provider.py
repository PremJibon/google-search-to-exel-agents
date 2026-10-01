import requests
from typing import List, Callable, Optional
from src.models import GeoBoundingBox, Lead
from src.providers.base import BusinessDataProvider
from src.services.normalizer import sanitize_phone, sanitize_url

class GooglePlacesProvider(BusinessDataProvider):
    """
    Optional official Google Places API (New) provider.
    Requires user to explicitly supply an API key. Never called without key.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key.strip()

    @property
    def name(self) -> str:
        return "Google Places API (Official)"

    @property
    def is_free(self) -> bool:
        return False  # Requires billing-enabled Google Cloud account

    def search(
        self,
        bbox: GeoBoundingBox,
        category: str,
        keyword: Optional[str] = None,
        max_results: int = 50,
        progress_callback: Optional[Callable[[int, str], None]] = None,
        location_name: Optional[str] = None,
        **kwargs
    ) -> List[Lead]:
        if not self.api_key:
            raise ValueError("Google Places API Key is missing. Please configure it in settings.")

        url = "https://places.googleapis.com/v1/places:searchText"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": (
                "places.id,places.displayName,places.formattedAddress,"
                "places.nationalPhoneNumber,places.internationalPhoneNumber,"
                "places.websiteUri,places.googleMapsUri,places.location"
            )
        }

        query_text = f"{category} {keyword or ''}".strip()
        payload = {
            "textQuery": query_text,
            "maxResultCount": min(max_results, 20),
            "locationRestriction": {
                "rectangle": {
                    "low": {"latitude": bbox.south, "longitude": bbox.west},
                    "high": {"latitude": bbox.north, "longitude": bbox.east}
                }
            }
        }

        if progress_callback:
            progress_callback(50, "Querying official Google Places API...")

        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code != 200:
            raise RuntimeError(f"Google Places API returned HTTP {response.status_code}: {response.text}")

        data = response.json()
        leads: List[Lead] = []

        for p in data.get("places", []):
            name = p.get("displayName", {}).get("text", "")
            if not name:
                continue

            phone = sanitize_phone(
                p.get("internationalPhoneNumber") or p.get("nationalPhoneNumber") or ""
            )
            website = sanitize_url(p.get("websiteUri") or "")
            address = p.get("formattedAddress", "")
            maps_link = p.get("googleMapsUri", "")
            loc = p.get("location", {})
            lat = loc.get("latitude")
            lon = loc.get("longitude")

            lead = Lead(
                business_name=name.strip(),
                phone=phone,
                address=address,
                website=website,
                maps_link=maps_link,
                category=category.title(),
                source="Google Places",
                status="FOUND" if phone else "MISSING_PHONE",
                lat=lat,
                lon=lon,
                raw_id=p.get("id", "")
            )
            leads.append(lead)

        return leads
