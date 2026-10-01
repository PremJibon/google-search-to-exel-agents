import math
import re
from typing import List
from src.models import Lead

def _haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two points on Earth in meters."""
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def _normalize_name_tokens(name: str) -> set:
    """Extracts alphanumeric words in lowercase for token comparison."""
    words = re.findall(r"\w+", name.lower())
    # Exclude common stop words
    stops = {"the", "and", "or", "of", "in", "at", "ltd", "pvt", "clinic", "center", "centre", "restaurant", "hotel", "cafe"}
    filtered = {w for w in words if w not in stops and len(w) > 1}
    return filtered if filtered else set(words)

def _name_similarity(name1: str, name2: str) -> float:
    """Calculates Jaccard similarity between token sets of two business names."""
    tokens1 = _normalize_name_tokens(name1)
    tokens2 = _normalize_name_tokens(name2)
    if not tokens1 or not tokens2:
        return 1.0 if name1.strip().lower() == name2.strip().lower() else 0.0
    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)
    return len(intersection) / len(union)

def deduplicate_leads(leads: List[Lead]) -> List[Lead]:
    """
    Deduplicates a list of leads using:
    1. Matching non-empty phone numbers
    2. Matching normalized website domains
    3. Proximity (<150m) + Name token similarity (>0.60)
    4. Exact raw OSM ID match
    Always preserves the richer record (e.g., has phone/website).
    """
    unique_leads: List[Lead] = []

    for candidate in leads:
        is_duplicate = False

        for i, existing in enumerate(unique_leads):
            # Check 1: Identical raw ID
            if candidate.raw_id and candidate.raw_id == existing.raw_id:
                is_duplicate = True
                break

            # Check 2: Matching phone number
            if candidate.phone and existing.phone and candidate.phone == existing.phone:
                is_duplicate = True
                # Merge richer data into existing
                if not existing.website and candidate.website:
                    existing.website = candidate.website
                if not existing.address and candidate.address:
                    existing.address = candidate.address
                break

            # Check 3: Matching website
            if candidate.website and existing.website and candidate.website == existing.website:
                is_duplicate = True
                if not existing.phone and candidate.phone:
                    existing.phone = candidate.phone
                break

            # Check 4: Geo-proximity + Name similarity
            if (candidate.lat is not None and candidate.lon is not None and 
                existing.lat is not None and existing.lon is not None):
                dist = _haversine_distance_meters(candidate.lat, candidate.lon, existing.lat, existing.lon)
                if dist < 150.0:
                    similarity = _name_similarity(candidate.business_name, existing.business_name)
                    if similarity >= 0.50:
                        is_duplicate = True
                        # Merge richer data
                        if not existing.phone and candidate.phone:
                            existing.phone = candidate.phone
                        if not existing.website and candidate.website:
                            existing.website = candidate.website
                        break

        if not is_duplicate:
            unique_leads.append(candidate)

    return unique_leads
