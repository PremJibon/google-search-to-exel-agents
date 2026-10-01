import re
from typing import List, Tuple

# Comprehensive taxonomy mapping natural categories to OSM key-value pairs
CATEGORY_MAPPINGS = {
    # Healthcare & Wellness
    "dental clinic": [("amenity", "dentist"), ("healthcare", "dentist"), ("amenity", "clinic")],
    "dentist": [("amenity", "dentist"), ("healthcare", "dentist")],
    "doctor": [("amenity", "doctors"), ("healthcare", "doctor"), ("amenity", "clinic")],
    "clinic": [("amenity", "clinic"), ("healthcare", "clinic"), ("amenity", "doctors")],
    "hospital": [("amenity", "hospital"), ("healthcare", "hospital")],
    "pharmacy": [("amenity", "pharmacy"), ("healthcare", "pharmacy")],
    "optician": [("shop", "optician")],
    "spa": [("leisure", "spa"), ("shop", "massage"), ("amenity", "spa")],

    # Fitness & Sports
    "gym": [("leisure", "fitness_centre"), ("leisure", "sports_centre"), ("amenity", "gym")],
    "fitness": [("leisure", "fitness_centre"), ("leisure", "sports_centre")],
    "sports club": [("leisure", "sports_centre"), ("club", "sport")],
    "yoga": [("leisure", "fitness_centre"), ("shop", "yoga")],

    # Food & Beverage
    "restaurant": [("amenity", "restaurant"), ("amenity", "fast_food"), ("amenity", "food_court")],
    "restaurants": [("amenity", "restaurant"), ("amenity", "fast_food")],
    "cafe": [("amenity", "cafe"), ("amenity", "coffee_shop")],
    "coffee": [("amenity", "cafe")],
    "bar": [("amenity", "bar"), ("amenity", "pub")],
    "bakery": [("shop", "bakery"), ("shop", "pastry")],
    "fast food": [("amenity", "fast_food")],

    # Retail & Shopping
    "supermarket": [("shop", "supermarket"), ("shop", "grocery")],
    "grocery": [("shop", "grocery"), ("shop", "supermarket"), ("shop", "convenience")],
    "pet shop": [("shop", "pet"), ("amenity", "pet_shop")],
    "clothing": [("shop", "clothes"), ("shop", "boutique")],
    "electronics": [("shop", "electronics"), ("shop", "computer"), ("shop", "mobile_phone")],
    "bookstore": [("shop", "books")],
    "jewellery": [("shop", "jewelry"), ("shop", "jewellery")],
    "hardware": [("shop", "hardware"), ("shop", "doityourself")],

    # Personal Services
    "salon": [("shop", "hairdresser"), ("shop", "beauty")],
    "hair salon": [("shop", "hairdresser")],
    "beauty salon": [("shop", "beauty"), ("shop", "hairdresser")],
    "laundry": [("shop", "laundry"), ("shop", "dry_cleaning")],

    # Hospitality
    "hotel": [("tourism", "hotel"), ("tourism", "motel"), ("tourism", "guest_house")],
    "hostel": [("tourism", "hostel")],
    "resort": [("tourism", "resort"), ("tourism", "hotel")],

    # Automotive & Professional Services
    "car repair": [("shop", "car_repair"), ("amenity", "car_wash")],
    "car wash": [("amenity", "car_wash")],
    "car dealer": [("shop", "car")],
    "bank": [("amenity", "bank"), ("amenity", "atm")],
    "lawyer": [("office", "lawyer")],
    "real estate": [("office", "estate_agent"), ("shop", "estate_agent")],
    "travel agency": [("shop", "travel_agency"), ("office", "travel_agent")],
    "school": [("amenity", "school"), ("amenity", "college")],
}

def get_osm_tags_for_category(category: str) -> List[Tuple[str, str]]:
    """
    Returns a list of (osm_key, osm_value) pairs matching the given category.
    If not explicitly found in taxonomy, returns generic business tags.
    """
    cleaned = category.lower().strip()
    
    # Exact lookup
    if cleaned in CATEGORY_MAPPINGS:
        return CATEGORY_MAPPINGS[cleaned]
    
    # Partial substring matching
    for key, tags in CATEGORY_MAPPINGS.items():
        if key in cleaned or cleaned in key:
            return tags
            
    # Generic fallback: Search across common commercial amenities and shops
    safe_val = re.sub(r"[^a-zA-Z0-9_]", "", cleaned.replace(" ", "_"))
    if safe_val:
        return [
            ("amenity", safe_val),
            ("shop", safe_val),
            ("office", safe_val),
            ("leisure", safe_val)
        ]
        
    return [("amenity", "restaurant"), ("shop", "convenience")]
