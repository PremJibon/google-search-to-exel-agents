import requests
from typing import List, Callable, Optional
from src.config import OVERPASS_SERVERS, OVERPASS_TIMEOUT, APP_USER_AGENT
from src.models import GeoBoundingBox, Lead
from src.providers.base import BusinessDataProvider
from src.services.synonym_mapper import get_osm_tags_for_category
from src.services.normalizer import sanitize_phone, sanitize_url, format_address_from_tags

class OpenStreetMapProvider(BusinessDataProvider):
    """
    100% Free, keyless business data provider querying OpenStreetMap via Overpass API.
    Features automated multi-mirror rotation for high availability.
    """

    @property
    def name(self) -> str:
        return "OpenStreetMap (Overpass API)"

    @property
    def is_free(self) -> bool:
        return True

    def _build_overpass_query(
        self,
        bbox: GeoBoundingBox,
        category: str,
        keyword: Optional[str] = None,
        max_results: int = 50
    ) -> str:
        """Constructs an optimized Overpass QL query string."""
        tags = get_osm_tags_for_category(category)
        bbox_str = bbox.to_overpass_bbox()

        query_blocks = []
        for k, v in tags:
            query_blocks.append(f'node["{k}"="{v}"]({bbox_str});')
            query_blocks.append(f'way["{k}"="{v}"]({bbox_str});')

        # If an additional keyword is provided, search by name match as well
        if keyword and keyword.strip():
            kw_clean = keyword.strip().replace('"', '\\"')
            query_blocks.append(f'node["name"~"{kw_clean}", i]({bbox_str});')
            query_blocks.append(f'way["name"~"{kw_clean}", i]({bbox_str});')

        joined_blocks = "\n  ".join(query_blocks)
        max_fetch = min(max(max_results * 3, 60), 150)
        return f"""[out:json][timeout:{OVERPASS_TIMEOUT}];
(
  {joined_blocks}
);
out center tags {max_fetch};"""

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
        query = self._build_overpass_query(bbox, category, keyword, max_results)
        headers = {
            "User-Agent": APP_USER_AGENT
        }

        data = None
        last_error = None

        # Mirror failover loop
        for mirror_index, server_url in enumerate(OVERPASS_SERVERS):
            try:
                if progress_callback:
                    progress_callback(
                        50,
                        f"Querying Overpass API (mirror {mirror_index + 1}/{len(OVERPASS_SERVERS)})..."
                    )

                response = requests.post(
                    server_url,
                    data={"data": query},
                    headers=headers,
                    timeout=OVERPASS_TIMEOUT
                )

                if response.status_code == 200 and response.text.strip().startswith("{"):
                    try:
                        parsed = response.json()
                        if parsed and "elements" in parsed:
                            data = parsed
                            break
                    except Exception:
                        pass
                elif response.status_code in (429, 502, 503, 504):
                    # Rate limit or gateway timeout on this mirror, try next
                    last_error = f"Server {server_url} returned status {response.status_code}"
                    continue
            except Exception as e:
                last_error = str(e)
                continue

        if not data or "elements" not in data:
            return []

        leads: List[Lead] = []
        for el in data.get("elements", []):
            tags = el.get("tags", {})
            name = tags.get("name") or tags.get("name:en") or tags.get("brand")
            
            # Skip unnamed POIs (e.g. anonymous buildings)
            if not name:
                continue

            # Phone collection from all potential OSM tags
            raw_phone = (
                tags.get("phone") or
                tags.get("contact:phone") or
                tags.get("contact:mobile") or
                tags.get("mobile") or
                tags.get("telephone") or
                ""
            )
            phone = sanitize_phone(raw_phone)

            # Website collection
            raw_website = (
                tags.get("website") or
                tags.get("contact:website") or
                tags.get("url") or
                ""
            )
            website = sanitize_url(raw_website)

            # Address compilation
            address = format_address_from_tags(tags)

            # Coordinates
            lat = el.get("lat") or el.get("center", {}).get("lat")
            lon = el.get("lon") or el.get("center", {}).get("lon")

            # Maps link
            el_type = el.get("type", "node")
            el_id = el.get("id", "")
            maps_link = f"https://www.openstreetmap.org/{el_type}/{el_id}" if el_id else ""

            lead = Lead(
                business_name=name.strip(),
                phone=phone,
                address=address,
                website=website,
                maps_link=maps_link,
                category=category.title(),
                source="OpenStreetMap",
                status="FOUND" if phone else "MISSING_PHONE",
                lat=lat,
                lon=lon,
                raw_id=f"{el_type}/{el_id}",
                tags=tags
            )
            leads.append(lead)

            if len(leads) >= max_results * 2:  # Fetch a surplus to account for dedup & phone filtering
                break

        return leads
