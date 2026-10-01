import math
import time
import requests
from typing import Optional
from src.config import NOMINATIM_BASE_URL, APP_USER_AGENT, GEOCODE_TIMEOUT
from src.models import GeoLocation, GeoBoundingBox

# Rate limiting tracker for Nominatim compliance (1 req / sec)
_last_request_time = 0.0

def _rate_limit():
    global _last_request_time
    now = time.time()
    elapsed = now - _last_request_time
    if elapsed < 1.1:
        time.sleep(1.1 - elapsed)
    _last_request_time = time.time()

def _create_radial_bbox(lat: float, lon: float, radius_km: float = 3.5) -> GeoBoundingBox:
    """Calculates a rectangular bounding box around a center lat/lon point."""
    lat_delta = radius_km / 111.0
    lon_delta = radius_km / (111.0 * max(0.1, math.cos(math.radians(lat))))
    return GeoBoundingBox(
        south=round(lat - lat_delta, 6),
        west=round(lon - lon_delta, 6),
        north=round(lat + lat_delta, 6),
        east=round(lon + lon_delta, 6)
    )

def geocode_location(country: str, city: str, area: str) -> Optional[GeoLocation]:
    """
    Geocodes area, city, country via OpenStreetMap Nominatim.
    If the specific area polygon is missing, gracefully falls back to city center with a 3.5km bounding box.
    """
    headers = {
        "User-Agent": APP_USER_AGENT,
        "Accept-Language": "en"
    }

    # Strategy 1: Specific query (Area + City + Country)
    query_parts = [p.strip() for p in [area, city, country] if p and p.strip()]
    if not query_parts:
        return None

    full_query = ", ".join(query_parts)
    
    _rate_limit()
    try:
        resp = requests.get(
            f"{NOMINATIM_BASE_URL}/search",
            params={"q": full_query, "format": "json", "limit": 1},
            headers=headers,
            timeout=GEOCODE_TIMEOUT
        )
        if resp.status_code == 200:
            data = resp.json()
            if data and len(data) > 0:
                item = data[0]
                lat = float(item["lat"])
                lon = float(item["lon"])
                bbox_raw = item.get("boundingbox")
                
                # Check if boundingbox is meaningful (not zero-size)
                if bbox_raw and len(bbox_raw) == 4:
                    s, n, w, e = float(bbox_raw[0]), float(bbox_raw[1]), float(bbox_raw[2]), float(bbox_raw[3])
                    # If bounding box is too tiny (single point), expand it
                    if abs(n - s) < 0.005 or abs(e - w) < 0.005:
                        bbox = _create_radial_bbox(lat, lon, radius_km=2.5)
                    else:
                        bbox = GeoBoundingBox(south=s, west=w, north=n, east=e)
                else:
                    bbox = _create_radial_bbox(lat, lon, radius_km=2.5)

                return GeoLocation(
                    display_name=item.get("display_name", full_query),
                    lat=lat,
                    lon=lon,
                    bounding_box=bbox,
                    is_fallback_radius=False
                )
    except Exception as e:
        # Logging or debug print can be added if needed
        pass

    # Strategy 2: Fallback query (Broader City + Country)
    if area and city:
        fallback_query = f"{city}, {country}".strip(", ")
        _rate_limit()
        try:
            resp = requests.get(
                f"{NOMINATIM_BASE_URL}/search",
                params={"q": fallback_query, "format": "json", "limit": 1},
                headers=headers,
                timeout=GEOCODE_TIMEOUT
            )
            if resp.status_code == 200:
                data = resp.json()
                if data and len(data) > 0:
                    item = data[0]
                    lat = float(item["lat"])
                    lon = float(item["lon"])
                    # Use a 4.0km radius around city center to cover the intended area
                    bbox = _create_radial_bbox(lat, lon, radius_km=4.0)
                    return GeoLocation(
                        display_name=f"{area} (near {item.get('display_name', fallback_query)})",
                        lat=lat,
                        lon=lon,
                        bounding_box=bbox,
                        is_fallback_radius=True
                    )
        except Exception:
            pass

    return None
