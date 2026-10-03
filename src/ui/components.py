import streamlit as st
import pandas as pd
from typing import List, Dict, Tuple
from src.models import Lead

# Predefined cascading location taxonomies
COUNTRY_PRESETS = [
    ("🇧🇩 Bangladesh", "Bangladesh"),
    ("🇮🇳 India", "India"),
    ("🇺🇸 United States", "United States"),
    ("🇬🇧 United Kingdom", "United Kingdom"),
    ("🇨🇦 Canada", "Canada"),
    ("🇦🇺 Australia", "Australia"),
    ("🇦🇪 United Arab Emirates", "United Arab Emirates"),
    ("🇸🇬 Singapore", "Singapore"),
    ("🇩🇪 Germany", "Germany"),
    ("🌍 Other / Custom Country", "Custom")
]

CITY_PRESETS_BY_COUNTRY: Dict[str, List[str]] = {
    "Bangladesh": [
        "Dhaka", "Chittagong", "Sylhet", "Rajshahi", "Khulna",
        "Kushtia", "Barisal", "Comilla", "Gazipur", "Narayanganj", "Custom City"
    ],
    "India": [
        "Bangalore", "Mumbai", "Delhi", "Kolkata", "Hyderabad",
        "Chennai", "Pune", "Ahmedabad", "Jaipur", "Custom City"
    ],
    "United States": [
        "New York", "Los Angeles", "Chicago", "Houston", "Austin",
        "Miami", "San Francisco", "Seattle", "Dallas", "Custom City"
    ],
    "United Kingdom": [
        "London", "Manchester", "Birmingham", "Leeds", "Glasgow",
        "Liverpool", "Edinburgh", "Bristol", "Custom City"
    ],
    "Canada": [
        "Toronto", "Vancouver", "Montreal", "Calgary", "Ottawa", "Custom City"
    ],
    "Australia": [
        "Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Custom City"
    ],
    "United Arab Emirates": [
        "Dubai", "Abu Dhabi", "Sharjah", "Ajman", "Custom City"
    ],
    "Singapore": [
        "Singapore", "Custom City"
    ],
    "Germany": [
        "Berlin", "Munich", "Hamburg", "Frankfurt", "Cologne", "Custom City"
    ],
    "Custom": ["Custom City"]
}

AREA_PRESETS_BY_CITY: Dict[str, List[str]] = {
    "Dhaka": [
        "Kamalapur", "Motijheel", "Dhanmondi", "Gulshan", "Banani",
        "Mirpur", "Uttara", "Wari", "Mohammadpur", "Badda", "Lalbagh", "Custom Area"
    ],
    "Chittagong": [
        "Agrabad", "GEC Circle", "Nasirabad", "Halishahar", "Panchlaish", "Custom Area"
    ],
    "Kushtia": [
        "Kushtia Sadar", "Thanapara", "NS Road", "Courtpara", "Majampur", "Custom Area"
    ],
    "Bangalore": [
        "Koramangala", "Indiranagar", "HSR Layout", "Whitefield",
        "Jayanagar", "MG Road", "Electronic City", "Custom Area"
    ],
    "Mumbai": [
        "Bandra", "Andheri", "Juhu", "Colaba", "Powai", "Dadar", "Custom Area"
    ],
    "Delhi": [
        "Connaught Place", "Hauz Khas", "Saket", "Karol Bagh", "Lajpat Nagar", "Custom Area"
    ],
    "New York": [
        "Manhattan", "Brooklyn", "Queens", "Williamsburg", "SoHo", "Custom Area"
    ],
    "London": [
        "Soho", "Camden", "City of London", "Westminster", "Kensington", "Custom Area"
    ],
    "Dubai": [
        "Downtown Dubai", "Dubai Marina", "Business Bay", "Deira", "Jumeirah", "Custom Area"
    ]
}

CATEGORY_PRESETS: List[Tuple[str, str]] = [
    ("🏋️ Gyms & Fitness Centers", "Gym"),
    ("🦷 Dental Clinics", "Dental Clinic"),
    ("🍽️ Restaurants & Cafes", "Restaurant"),
    ("💇 Salons, Spas & Beauty", "Salon"),
    ("🚗 Car Repair & Wash", "Car Repair"),
    ("🏥 Doctors & Medical Clinics", "Clinic"),
    ("🏢 Real Estate Agencies", "Real Estate"),
    ("🏨 Hotels & Stays", "Hotel"),
    ("🛒 Retail & Supermarkets", "Supermarket"),
    ("✏️ Custom Category...", "Custom")
]

from src.ui.responsive_styles import inject_responsive_saas_styles

def inject_custom_styles():
    """Injects high-end, modern SaaS CSS styling for the Streamlit dashboard."""
    inject_responsive_saas_styles()

def render_metric_cards(total_found: int, filtered_count: int, phone_count: int, high_opp_count: int, duration: float):
    """Renders responsive modern SaaS metric cards that adapt across mobile (2-col), tablet (3-col), and desktop (5-col)."""
    grid_html = f"""
    <div class="responsive-metrics-grid">
        <div class="metric-card">
            <div class="metric-value">{total_found}</div>
            <div class="metric-label">🔭 Discovered POIs</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" style="color: #38BDF8;">{filtered_count}</div>
            <div class="metric-label">📋 Matching Leads</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" style="color: #10B981;">{high_opp_count}</div>
            <div class="metric-label">🔥 High Priority</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" style="color: #F59E0B;">{phone_count}</div>
            <div class="metric-label">📞 With Phone</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{duration}s</div>
            <div class="metric-label">⚡ Execution Time</div>
        </div>
    </div>
    """
    st.markdown(grid_html, unsafe_allow_html=True)

def leads_to_dataframe(leads: List[Lead]) -> pd.DataFrame:
    """Converts lead objects to a clean display DataFrame."""
    if not leads:
        return pd.DataFrame(columns=[
            "Business Name", "Phone", "Address", "Website", "Lead Score", "Opportunity", "Suggested Service", "Pitch Angle", "Maps Link", "Category", "Source"
        ])
    data = [lead.to_export_dict() for lead in leads]
    return pd.DataFrame(data)
