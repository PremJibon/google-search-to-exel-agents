import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import folium
import re
from src.models import Lead

lead = Lead(
    business_name="Test Gym",
    phone="01715698888",
    address="Gulshan, Dhaka",
    website="https://testgym.com",
    maps_link="https://maps.google.com",
    category="Gym",
    source="Tavily",
    status="FOUND",
    lat=23.792,
    lon=90.415,
    lead_score="HIGH",
    opportunity_type="No Mobile Booking",
    suggested_service="Custom Booking Site"
)

m = folium.Map(location=[23.792, 90.415], zoom_start=13)
folium.Marker([23.792, 90.415], popup="Test Popup", icon=folium.Icon(color="red", icon="info-sign")).add_to(m)
print("Folium map rendered with markers OK")

from src.ui.google_map_component import render_google_map_html
from src.config import GOOGLE_MAPS_API_KEY

html = render_google_map_html(
    api_key=GOOGLE_MAPS_API_KEY,
    center_lat=23.792,
    center_lon=90.415,
    zoom=13,
    leads=[lead],
    marked_lat=23.792,
    marked_lon=90.415,
    radius_km=3.0
)

assert GOOGLE_MAPS_API_KEY in html, "API key should be present in generated HTML"
assert "Test Gym" in html, "Lead name should be present in markersData"
assert "https://api.whatsapp.com/send?phone=8801715698888" in html, "Formatted WhatsApp link should be present"
print("Google Maps JS API component generated and validated OK!")

