import streamlit as st
import pandas as pd
from typing import List
from src.models import Lead

def inject_custom_styles():
    """Injects clean, professional CSS styling for the Streamlit dashboard."""
    st.markdown("""
        <style>
        /* Modern font and container styling */
        .main-header {
            font-size: 2.2rem;
            font-weight: 700;
            color: #1E293B;
            margin-bottom: 0.2rem;
        }
        .sub-header {
            font-size: 1.05rem;
            color: #64748B;
            margin-bottom: 1.5rem;
        }
        /* Custom metric card */
        .metric-card {
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: bold;
            color: #0F172A;
        }
        .metric-label {
            font-size: 0.85rem;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        /* Button styling */
        .stButton>button {
            border-radius: 6px;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)

def render_metric_cards(total_found: int, filtered_count: int, phone_count: int, high_opp_count: int, duration: float):
    """Renders 5 responsive summary metric cards."""
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_found}</div>
                <div class="metric-label">Discovered POIs</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{filtered_count}</div>
                <div class="metric-label">Matching Leads</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #10B981;">{high_opp_count}</div>
                <div class="metric-label">High Opportunities</div>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{phone_count}</div>
                <div class="metric-label">With Phone</div>
            </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{duration}s</div>
                <div class="metric-label">Duration</div>
            </div>
        """, unsafe_allow_html=True)

def leads_to_dataframe(leads: List[Lead]) -> pd.DataFrame:
    """Converts lead objects to a clean display DataFrame."""
    if not leads:
        return pd.DataFrame(columns=[
            "Business Name", "Phone", "Address", "Website", "Maps Link", "Category", "Source"
        ])
    data = [lead.to_export_dict() for lead in leads]
    return pd.DataFrame(data)
