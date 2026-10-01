import streamlit as st
import pandas as pd
from datetime import datetime
from src.config import APP_NAME, VERSION, GOOGLE_MAPS_API_KEY
from src.models import SearchParams
from src.pipelines.lead_pipeline import LeadPipeline
from src.providers.osm_provider import OpenStreetMapProvider
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
        options=["OpenStreetMap (100% Free)", "Google Places API (Optional)"],
        index=0,
        help="OpenStreetMap is 100% free and requires no API key or credit card."
    )

    google_api_key = ""
    if "Google Places" in provider_choice:
        google_api_key = st.text_input(
            "Google Places API Key",
            value=GOOGLE_MAPS_API_KEY,
            type="password",
            help="Enter your official Google Cloud API key with Places API (New) enabled."
        )
        if not google_api_key:
            st.warning("⚠️ API Key required for Google Places. Defaulting to OpenStreetMap if empty.")

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
    '<div class="sub-header">Discover local business leads, phone numbers, and addresses with 100% free open data.</div>',
    unsafe_allow_html=True
)

# Search Input Form
with st.form(key="search_form"):
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

    submit_button = st.form_submit_button("🚀 Find Local Businesses", use_container_width=True)

# Search Execution
if submit_button:
    if not country.strip() or not city.strip() or not area.strip() or not category.strip():
        st.error("Please fill in Country, City, Area, and Business Category before searching.")
    else:
        # Determine active provider
        if "Google Places" in provider_choice and google_api_key.strip():
            selected_provider = GooglePlacesProvider(api_key=google_api_key.strip())
        else:
            selected_provider = OpenStreetMapProvider()

        pipeline = LeadPipeline(provider=selected_provider)
        params = SearchParams(
            country=country.strip(),
            city=city.strip(),
            area=area.strip(),
            category=category.strip(),
            keyword=keyword.strip() if keyword.strip() else None,
            limit=int(max_results),
            require_phone=require_phone,
            require_website=require_website
        )

        progress_container = st.empty()
        status_container = st.empty()

        def on_progress(percent: int, message: str):
            progress_container.progress(percent / 100.0)
            status_container.info(f"⏳ **Step**: {message}")

        try:
            with st.spinner("Finding leads..."):
                result = pipeline.run(params, progress_callback=on_progress)
                st.session_state.search_result = result
                st.session_state.current_params = params

            progress_container.empty()
            status_container.empty()
            st.success(f"✅ Found {len(result.leads)} matching leads in {result.duration_seconds}s!")

        except Exception as e:
            progress_container.empty()
            status_container.empty()
            st.error(f"❌ Search Error: {str(e)}")

# Display Results & Export
if st.session_state.search_result:
    res = st.session_state.search_result
    params = st.session_state.current_params

    st.markdown("---")
    st.subheader(f"📊 Search Results for '{params.category}' in {params.area}, {params.city}")

    # Display warning/guidance if any
    if res.warning_message:
        st.warning(f"ℹ️ {res.warning_message}")

    # Metrics
    phone_count = sum(1 for lead in res.leads if lead.phone)
    render_metric_cards(
        total_found=res.total_found,
        filtered_count=res.filtered_count,
        phone_count=phone_count,
        duration=res.duration_seconds
    )

    st.write("")

    if res.leads:
        df = leads_to_dataframe(res.leads)

        # Action bar & Export buttons
        excel_data = export_to_excel(res.leads)
        csv_data = export_to_csv(res.leads)
        excel_filename = create_safe_filename(params.category, params.area, params.city, "xlsx")
        csv_filename = create_safe_filename(params.category, params.area, params.city, "csv")

        col_dl1, col_dl2, col_space = st.columns([1.5, 1.5, 3])
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
                "Phone": st.column_config.TextColumn(width="small"),
                "Address": st.column_config.TextColumn(width="large"),
                "Website": st.column_config.LinkColumn(width="medium"),
                "Maps Link": st.column_config.LinkColumn(width="small"),
                "Category": st.column_config.TextColumn(width="small"),
                "Source": st.column_config.TextColumn(width="small")
            },
            hide_index=True
        )
    else:
        st.info("No leads available to display. Try broadening your location or category filters.")
