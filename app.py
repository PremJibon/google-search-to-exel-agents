import streamlit as st
import pandas as pd
from datetime import datetime
from src.config import APP_NAME, VERSION, GOOGLE_MAPS_API_KEY, SERPER_API_KEY, TAVILY_API_KEY, OPENROUTER_API_KEY
from src.models import SearchParams
from src.pipelines.lead_pipeline import LeadPipeline
from src.providers.osm_provider import OpenStreetMapProvider
from src.providers.serper_provider import SerperGoogleMapsProvider
from src.providers.google_provider import GooglePlacesProvider
from src.services.exporter import export_to_excel, export_to_csv, create_safe_filename
from src.ui.components import inject_custom_styles, render_metric_cards, leads_to_dataframe

# Set Streamlit Page Configuration
st.set_page_config(
    page_title=f"{APP_NAME} - Free Lead Generator",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_custom_styles()

# Initialize session state for persistent results
if "search_result" not in st.session_state:
    st.session_state.search_result = None
if "current_params" not in st.session_state:
    st.session_state.current_params = None

# Sidebar Configuration
with st.sidebar:
    st.title("⚙️ Provider & Settings")
    
    provider_choice = st.radio(
        "Active Data Provider",
        options=[
            "Google Maps via Serper (2,500 Free)",
            "OpenStreetMap (100% Free - Keyless)",
            "Google Cloud Places API (Optional)"
        ],
        index=0 if SERPER_API_KEY else 1,
        help="Google Maps via Serper delivers verified Google phone numbers and addresses. OpenStreetMap is 100% free with no key required."
    )

    serper_api_key = ""
    google_api_key = ""

    if "Serper" in provider_choice:
        serper_api_key = st.text_input(
            "Serper API Key",
            value=SERPER_API_KEY,
            type="password",
            help="Get 2,500 free Google Maps searches at https://serper.dev (no credit card required)."
        )
        if not serper_api_key:
            st.info("💡 Enter your free Serper API key to query Google Maps directly, or select OpenStreetMap below.")

    elif "Google Cloud" in provider_choice:
        google_api_key = st.text_input(
            "Google Places API Key",
            value=GOOGLE_MAPS_API_KEY,
            type="password",
            help="Enter your official Google Cloud API key with Places API (New) enabled."
        )
        if not google_api_key:
            st.warning("⚠️ API Key required for Google Cloud Places. Defaulting to OpenStreetMap if empty.")

    st.markdown("---")
    st.subheader("🔍 Web Intelligence (Optional)")
    tavily_key = st.text_input(
        "Tavily Search API Key",
        value=TAVILY_API_KEY,
        type="password",
        help="Optional: Free tier offers 1,000 searches/mo. Used to verify websites and search web footprints."
    )

    st.markdown("---")
    st.markdown("### 📋 Responsible Use Notice")
    st.caption(
        "This tool extracts publicly available business information for legitimate B2B prospecting. "
        "Please respect local communication regulations such as India's TRAI DND registry, GDPR in Europe, "
        "and TCPA in the US. Do not engage in automated spam."
    )
    st.caption(f"v{VERSION} • Free & Open-Source")

# Main Interface
st.markdown(f'<div class="main-header">📍 {APP_NAME}</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Discover local business leads, audit digital presence, and generate custom agency sales pitches.</div>',
    unsafe_allow_html=True
)

# Search Input Form
with st.form(key="search_form"):
    st.markdown("##### 1. Your Agency Target Goal")
    agency_goal = st.selectbox(
        "What services do you want to offer to these businesses?",
        options=[
            "Website Development",
            "AI Automation / Chatbots",
            "Local SEO / Google Maps",
            "General B2B Outreach"
        ],
        index=0,
        help="Agent 2 will audit each lead and prepare custom sales angles based on your agency service."
    )

    st.markdown("##### 2. Target Location & Category")
    col1, col2, col3 = st.columns(3)
    with col1:
        country = st.text_input("Country", value="India", placeholder="e.g. India, Bangladesh, USA")
    with col2:
        city = st.text_input("City / District", value="Bangalore", placeholder="e.g. Bangalore, Dhaka, New York")
    with col3:
        area = st.text_input("Area / Neighborhood", value="Koramangala", placeholder="e.g. Koramangala, Dhanmondi, Downtown")

    col4, col5, col6 = st.columns([2, 1, 1])
    with col4:
        category = st.text_input("Business Category", value="Restaurants", placeholder="e.g. Dental clinics, Gyms, Restaurants, Pet shops")
    with col5:
        keyword = st.text_input("Optional Keyword", value="", placeholder="e.g. Vegetarian, 24/7")
    with col6:
        max_results = st.number_input("Max Results", min_value=5, max_value=200, value=50, step=5)

    col7, col8 = st.columns(2)
    with col7:
        require_phone = st.checkbox("Require Phone Number (hide leads without phone)", value=False)
    with col8:
        require_website = st.checkbox("Require Website", value=False)

    submit_button = st.form_submit_button("🚀 Launch 2-Agent Lead & Audit Search", use_container_width=True)

# Search Execution
if submit_button:
    if not country.strip() or not city.strip() or not area.strip() or not category.strip():
        st.error("Please fill in Country, City, Area, and Business Category before searching.")
    else:
        # Determine active provider
        if "Serper" in provider_choice and serper_api_key.strip():
            selected_provider = SerperGoogleMapsProvider(api_key=serper_api_key.strip())
        elif "Google Cloud" in provider_choice and google_api_key.strip():
            selected_provider = GooglePlacesProvider(api_key=google_api_key.strip())
        else:
            selected_provider = OpenStreetMapProvider()

        pipeline = LeadPipeline(provider=selected_provider, tavily_key=tavily_key.strip())
        params = SearchParams(
            country=country.strip(),
            city=city.strip(),
            area=area.strip(),
            category=category.strip(),
            keyword=keyword.strip() if keyword.strip() else None,
            limit=int(max_results),
            require_phone=require_phone,
            require_website=require_website,
            agency_goal=agency_goal
        )

        progress_container = st.empty()
        status_container = st.empty()

        def on_progress(percent: int, message: str):
            progress_container.progress(percent / 100.0)
            status_container.info(f"⏳ **Step**: {message}")

        try:
            with st.spinner("Executing discovery & qualification pipeline..."):
                result = pipeline.run(params, progress_callback=on_progress)
                st.session_state.search_result = result
                st.session_state.current_params = params

            progress_container.empty()
            status_container.empty()
            st.success(f"✅ Found & audited {len(result.leads)} leads in {result.duration_seconds}s!")

        except Exception as e:
            progress_container.empty()
            status_container.empty()
            st.error(f"❌ Search Error: {str(e)}")

# Display Results & Export
if st.session_state.search_result:
    res = st.session_state.search_result
    params = st.session_state.current_params

    st.markdown("---")
    st.subheader(f"📊 Qualified Leads for '{params.category}' in {params.area}, {params.city}")
    st.caption(f"🎯 Target Agency Goal: **{params.agency_goal}**")

    # Display warning/guidance if any
    if res.warning_message:
        st.warning(f"ℹ️ {res.warning_message}")

    # Metrics
    phone_count = sum(1 for lead in res.leads if lead.phone)
    high_opp_count = sum(1 for lead in res.leads if lead.lead_score == "HIGH")
    render_metric_cards(
        total_found=res.total_found,
        filtered_count=res.filtered_count,
        phone_count=phone_count,
        high_opp_count=high_opp_count,
        duration=res.duration_seconds
    )

    st.write("")

    if res.leads:
        tab1, tab2 = st.tabs(["📋 Qualified Leads & Export", "🗺️ Geographic Map Preview"])

        with tab1:
            col_filter, col_dl1, col_dl2 = st.columns([2, 1.5, 1.5])
            with col_filter:
                score_filter = st.selectbox(
                    "Filter by Opportunity Score:",
                    options=["All Leads", "HIGH Priority Only", "MEDIUM & HIGH Only"]
                )

            # Filter data based on selection
            if score_filter == "HIGH Priority Only":
                display_leads = [l for l in res.leads if l.lead_score == "HIGH"]
            elif score_filter == "MEDIUM & HIGH Only":
                display_leads = [l for l in res.leads if l.lead_score in ("HIGH", "MEDIUM")]
            else:
                display_leads = res.leads

            df = leads_to_dataframe(display_leads)

            # Export data based on displayed leads
            excel_data = export_to_excel(display_leads)
            csv_data = export_to_csv(display_leads)
            excel_filename = create_safe_filename(f"{params.category}_{params.agency_goal}", params.area, params.city, "xlsx")
            csv_filename = create_safe_filename(f"{params.category}_{params.agency_goal}", params.area, params.city, "csv")

            with col_dl1:
                st.download_button(
                    label="📥 Download Excel (.xlsx)",
                    data=excel_data,
                    file_name=excel_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            with col_dl2:
                st.download_button(
                    label="📥 Download CSV (.csv)",
                    data=csv_data,
                    file_name=csv_filename,
                    mime="text/csv",
                    use_container_width=True
                )

            # Interactive Table with column configuration
            st.dataframe(
                df,
                use_container_width=True,
                column_config={
                    "Business Name": st.column_config.TextColumn(width="medium"),
                    "Lead Score": st.column_config.TextColumn(width="small"),
                    "Opportunity": st.column_config.TextColumn(width="medium"),
                    "Suggested Service": st.column_config.TextColumn(width="medium"),
                    "Pitch Angle": st.column_config.TextColumn(width="large"),
                    "Phone": st.column_config.TextColumn(width="small"),
                    "Address": st.column_config.TextColumn(width="medium"),
                    "Website": st.column_config.LinkColumn(width="medium"),
                    "Maps Link": st.column_config.LinkColumn(width="small"),
                    "Category": st.column_config.TextColumn(width="small"),
                    "Source": st.column_config.TextColumn(width="small")
                },
                hide_index=True
            )

        with tab2:
            # Map preview for leads with valid coordinates
            map_data = [
                {"lat": lead.lat, "lon": lead.lon, "name": lead.business_name}
                for lead in display_leads
                if lead.lat is not None and lead.lon is not None
            ]
            if map_data:
                map_df = pd.DataFrame(map_data)
                st.map(map_df, latitude="lat", longitude="lon", size=20, zoom=13)
                st.caption(f"Showing {len(map_df)} geolocated business leads on map.")
            else:
                st.info("No geographic coordinates available for the current leads.")
    else:
        st.info("No leads available to display. Try broadening your location or category filters.")
