from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List

@dataclass
class GeoBoundingBox:
    south: float
    west: float
    north: float
    east: float

    def to_overpass_bbox(self) -> str:
        """Returns south,west,north,east format for Overpass QL."""
        return f"{self.south},{self.west},{self.north},{self.east}"

@dataclass
class GeoLocation:
    display_name: str
    lat: float
    lon: float
    bounding_box: GeoBoundingBox
    is_fallback_radius: bool = False

@dataclass
class SearchParams:
    country: str
    city: str
    area: str
    category: str
    keyword: Optional[str] = None
    limit: int = 50
    require_phone: bool = False
    require_website: bool = False
    agency_goal: str = "Website Development"  # "Website Development", "AI Automation / Chatbots", "General Lead Generation"

@dataclass
class Lead:
    business_name: str
    phone: str = ""
    address: str = ""
    website: str = ""
    maps_link: str = ""
    category: str = ""
    source: str = "OpenStreetMap"
    status: str = "FOUND"
    lat: Optional[float] = None
    lon: Optional[float] = None
    raw_id: str = ""
    tags: Dict[str, Any] = field(default_factory=dict)
    
    # Agency Qualification Fields (Agent 2)
    lead_score: str = "MEDIUM"        # HIGH, MEDIUM, LOW
    opportunity_type: str = ""        # e.g. "No Website", "Social Only Website", "High-Volume Booking Need"
    suggested_service: str = ""       # e.g. "Custom Website Design", "AI Receptionist / Chatbot"
    pitch_angle: str = ""             # e.g. "Pitch a responsive website with online ordering"

    def to_export_dict(self) -> Dict[str, str]:
        return {
            "Business Name": self.business_name,
            "Phone": self.phone,
            "Address": self.address,
            "Website": self.website,
            "Lead Score": self.lead_score,
            "Opportunity": self.opportunity_type,
            "Suggested Service": self.suggested_service,
            "Pitch Angle": self.pitch_angle,
            "Maps Link": self.maps_link,
            "Category": self.category,
            "Source": self.source
        }

@dataclass
class SearchResult:
    leads: List[Lead]
    total_found: int
    filtered_count: int
    duration_seconds: float
    location_used: Optional[GeoLocation] = None
    warning_message: Optional[str] = None
