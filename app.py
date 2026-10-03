import streamlit as st
import pandas as pd
import gc
import time
import re
import folium
from streamlit_folium import st_folium
from datetime import datetime
from src.config import (
    APP_NAME, VERSION, GOOGLE_MAPS_API_KEY, SERPER_API_KEY,
    TAVILY_API_KEY, OPENROUTER_API_KEY, BAZAARLINK_BASE_URL, BAZAARLINK_API_KEY,
    GROQ_API_KEY
)
from src.models import SearchParams, SearchResult, Lead
from src.pipelines.lead_pipeline import LeadPipeline
from src.providers.osm_provider import OpenStreetMapProvider
from src.providers.serper_provider import SerperGoogleMapsProvider
from src.providers.google_provider import GooglePlacesProvider
from src.providers.tavily_provider import TavilySearchProvider
from src.services.exporter import export_to_excel, export_to_csv, create_safe_filename
from src.services.agent_chat import agent_chat_service, AGENT_PROFILES
from src.services.llm_helper import llm_helper
import streamlit.components.v1 as components
from src.ui.google_map_component import render_google_map_html
from src.services.geocoding import geocode_location, reverse_geocode, create_radial_bbox
from src.services.agency_qualifier import qualify_leads_batch
from src.services.security import (
    verify_access_password,
    is_auth_enabled,
    check_search_cooldown,
    sanitize_html_text
)
from src.ui.components import (
    inject_custom_styles,
    render_metric_cards,
    leads_to_dataframe,
    COUNTRY_PRESETS,
    CITY_PRESETS_BY_COUNTRY,
    AREA_PRESETS_BY_CITY,
    CATEGORY_PRESETS
)
from src.ui.voice_component import render_voice_input_widget, render_browser_voice_dictation, render_whisper_voice_recorder
from src.ui.responsive_styles import inject_responsive_saas_styles

# Set Streamlit Page Configuration
st.set_page_config(
    page_title=f"{APP_NAME} - Agency Lead Finder & Multi-Agent Co-Pilot",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_custom_styles()

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = not is_auth_enabled()
if "last_search_time" not in st.session_state:
    st.session_state.last_search_time = 0.0
if "search_result" not in st.session_state:
    st.session_state.search_result = None
if "current_params" not in st.session_state:
    st.session_state.current_params = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "selected_agent" not in st.session_state:
    st.session_state.selected_agent = "Apex"
if "selected_map_pin" not in st.session_state:
    st.session_state.selected_map_pin = None
if "selected_pin_name" not in st.session_state:
    st.session_state.selected_pin_name = ""
if "marked_location" not in st.session_state:
    st.session_state.marked_location = None
if "last_recorded_click" not in st.session_state:
    st.session_state.last_recorded_click = None

# Zero-Trust Master Passkey Gatekeeper
if not st.session_state.authenticated:
    st.markdown("""
        <div class="saas-hero">
            <div class="saas-title">🔒 Agency Portal — Protected Access</div>
            <div class="saas-subtitle">Enter your Agency Master Passkey to unlock LeadFinder and the AI Agent Co-Pilot.</div>
        </div>
    """, unsafe_allow_html=True)
    with st.form("auth_form"):
        col_auth1, col_auth2 = st.columns([3, 1])
        with col_auth1:
            entered_key = st.text_input("Master Passkey / PIN", type="password", placeholder="Enter agency passkey...")
        with col_auth2:
            st.write("")
            st.write("")
            submit_auth = st.form_submit_button("🔓 Unlock Portal", use_container_width=True)

        if submit_auth:
            if verify_access_password(entered_key):
                st.session_state.authenticated = True
                st.success("✅ Access Granted! Redirecting...")
                st.rerun()
            else:
                st.error("❌ Invalid Access Passkey. Access Denied.")
    st.caption("🛡️ Protected by Zero-Trust Gatekeeper • Anti-DDoS & Secret Vault Active")
    st.stop()

# Clean Sidebar Configuration (Without cluttered API Key inputs)
with st.sidebar:
    st.markdown("### ⚙️ Search Provider")

    provider_options = ["OpenStreetMap (100% Free - Keyless)"]
    if TAVILY_API_KEY:
        provider_options.append("Tavily Web & Google Search (Live AI Discovery)")
    if SERPER_API_KEY:
        provider_options.append("Google Maps via Serper (2,500 Free)")
    if GOOGLE_MAPS_API_KEY:
        provider_options.append("Google Cloud Places API (Optional)")

    def_prov_idx = 0
    if TAVILY_API_KEY and "Tavily Web & Google Search (Live AI Discovery)" in provider_options:
        def_prov_idx = provider_options.index("Tavily Web & Google Search (Live AI Discovery)")
    elif SERPER_API_KEY and "Google Maps via Serper (2,500 Free)" in provider_options:
        def_prov_idx = provider_options.index("Google Maps via Serper (2,500 Free)")

    provider_choice = st.radio(
        "Active Data Provider",
        options=provider_options,
        index=def_prov_idx,
        help="OpenStreetMap is 100% free with no key required. Tavily Web Search and Google Maps deliver verified contact numbers and live website auditing."
    )

    serper_api_key = SERPER_API_KEY
    google_api_key = GOOGLE_MAPS_API_KEY

    st.markdown("---")
    st.markdown("### 🤖 Active Agent Team")
    st.markdown("""
        <div class="agent-pill pill-nova">🔭 Nova • Lead Discovery</div>
        <div class="agent-pill pill-max">🔍 Max • Tech Auditor</div>
        <div class="agent-pill pill-apex">📢 Apex • Digital Marketer</div>
        <div class="agent-pill pill-atlas">🧭 Atlas • Agency Mentor</div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption(
        "This tool extracts public business info for legitimate B2B prospecting. "
        "Respect local compliance (TRAI DND, GDPR, TCPA). Do not spam."
    )
    st.caption(f"v{VERSION} • SaaS Edition • Powered by Groq ⚡")

    if is_auth_enabled():
        st.markdown("---")
        if st.button("🔒 Logout Portal", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

# Main SaaS Hero Header
st.markdown("""
    <div class="saas-hero">
        <div class="saas-title">📍 LeadFinder Agency Co-Pilot</div>
        <div class="saas-subtitle">
            Autonomous multi-agent system: <strong>Nova</strong> discovers local businesses, <strong>Max</strong> audits digital gaps, 
            and <strong>Apex</strong> (Digital Marketer) crafts high-converting sales pitches and client acquisition campaigns.
        </div>
        <div class="agent-pills-wrap">
            <span class="agent-pill pill-nova">🔭 Nova (Discovery)</span>
            <span class="agent-pill pill-max">🔍 Max (Tech Audit)</span>
            <span class="agent-pill pill-apex">📢 Apex (Digital Marketer)</span>
            <span class="agent-pill pill-atlas">🧭 Atlas (Strategy)</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Top-Level SaaS Tabs (ALWAYS ACCESSIBLE!)
main_tab1, main_tab2, main_tab3 = st.tabs([
    "🚀 Lead Discovery & Audit",
    "💬 Agency Multi-Agent Chatroom",
    "🗺️ Geographic Map Preview"
])

# ========================================================
# TAB 1: LEAD DISCOVERY & AUDIT
# ========================================================
with main_tab1:
    with st.expander("🎙️ Voice Search Assistant (Speak Business Niche or Location)", expanded=False):
        voice_query = render_voice_input_widget(
            key="tab1_voice_search",
            label="🎙️ Speak target business niche or location (e.g. 'Dental clinics in Dhanmondi')",
            button_label="🔍 Send Voice Query to Agency Chatroom"
        )
        if voice_query:
            st.session_state.chat_history.append({"role": "user", "content": voice_query})
            st.success(f"🎙️ Query captured: **\"{voice_query}\"** — Head to **💬 Agency Multi-Agent Chatroom** to view audited leads!")

    with st.form(key="search_form"):
        st.markdown("##### 1. Your Agency Target Goal")
        agency_goal = st.selectbox(
            "What high-ticket service do you want to offer to these businesses?",
            options=[
                "Website Development",
                "AI Automation / Chatbots",
                "Local SEO / Google Maps",
                "General B2B Outreach"
            ],
            index=0,
            help="Agent Max and Agent Apex customize audits and cold outreach copy based on this service goal."
        )

        st.markdown("##### 2. Location Selection (Smart Cascading Dropdowns)")
        col_c1, col_c2, col_c3 = st.columns(3)

        # 1. Country Selection
        with col_c1:
            country_labels = [label for label, _ in COUNTRY_PRESETS]
            selected_country_label = st.selectbox(
                "Country",
                options=country_labels,
                index=0, # Default Bangladesh
                help="Select your target country. City and area suggestions will automatically adapt."
            )
            canonical_country = next(val for lbl, val in COUNTRY_PRESETS if lbl == selected_country_label)
            if canonical_country == "Custom":
                target_country = st.text_input("Enter Custom Country", value="Bangladesh")
            else:
                target_country = canonical_country

        # 2. City Selection
        with col_c2:
            available_cities = CITY_PRESETS_BY_COUNTRY.get(target_country, ["Custom City"])
            selected_city_choice = st.selectbox(
                "City / District",
                options=available_cities,
                index=0,
                help="Select target city or choose 'Custom City' to type your own."
            )
            if selected_city_choice == "Custom City":
                target_city = st.text_input("Enter Custom City", value="Dhaka")
            else:
                target_city = selected_city_choice

        # 3. Area / Neighborhood Selection
        with col_c3:
            available_areas = AREA_PRESETS_BY_CITY.get(target_city, ["Custom Area"])
            if "Custom Area" not in available_areas:
                available_areas.append("Custom Area")

            selected_area_choice = st.selectbox(
                "Area / Neighborhood",
                options=available_areas,
                index=0,
                help="Select neighborhood or choose 'Custom Area' to type your own."
            )
            if selected_area_choice == "Custom Area":
                target_area = st.text_input("Enter Custom Area / Neighborhood", value="Kamalapur")
            else:
                target_area = selected_area_choice

        st.markdown("##### 3. Category & Nuance")
        col_cat1, col_cat2, col_cat3 = st.columns([2, 1, 1])

        with col_cat1:
            category_labels = [label for label, _ in CATEGORY_PRESETS]
            selected_cat_label = st.selectbox(
                "Business Category",
                options=category_labels,
                index=0, # Default Gym
                help="Choose a pre-mapped business category or select 'Custom Category'."
            )
            canonical_category = next(val for lbl, val in CATEGORY_PRESETS if lbl == selected_cat_label)
            if canonical_category == "Custom":
                target_category = st.text_input("Enter Custom Category", value="Gym")
            else:
                target_category = canonical_category

        with col_cat2:
            keyword = st.text_input("Optional Keyword", value="", placeholder="e.g. 24/7, Ladies, Luxury")
        with col_cat3:
            max_results = st.number_input("Max Results", min_value=5, max_value=100, value=25, step=5)

        col_flt1, col_flt2 = st.columns(2)
        with col_flt1:
            require_phone = st.checkbox("Require Phone Number (hide leads without phone)", value=False)
            st.caption("💡 Tip: Leave unchecked in Bangladesh/India to view all businesses; Deep Search will enrich contact details automatically.")
        with col_flt2:
            require_website = st.checkbox("Require Website", value=False)

        submit_button = st.form_submit_button("🚀 Launch Multi-Agent Lead & Audit Search", use_container_width=True)

    # Search Execution
    if submit_button:
        can_search, wait_s = check_search_cooldown(st.session_state.last_search_time, cooldown_seconds=4.0)
        if not can_search:
            st.warning(f"⏳ Security Cooldown Active: Please wait {wait_s}s before submitting another search query to protect system resources.")
        elif not target_country.strip() or not target_city.strip() or not target_area.strip() or not target_category.strip():
            st.error("Please ensure Country, City, Area, and Business Category are filled before searching.")
        else:
            st.session_state.last_search_time = time.time()
            # Determine active provider
            if "Tavily" in provider_choice and TAVILY_API_KEY:
                selected_provider = TavilySearchProvider(api_key=TAVILY_API_KEY)
            elif "Serper" in provider_choice and serper_api_key.strip():
                selected_provider = SerperGoogleMapsProvider(api_key=serper_api_key.strip())
            elif "Google Cloud" in provider_choice and google_api_key.strip():
                selected_provider = GooglePlacesProvider(api_key=google_api_key.strip())
            else:
                selected_provider = OpenStreetMapProvider()

            pipeline = LeadPipeline(provider=selected_provider, tavily_key=TAVILY_API_KEY)
            params = SearchParams(
                country=target_country.strip(),
                city=target_city.strip(),
                area=target_area.strip(),
                category=target_category.strip(),
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
                status_container.info(f"⏳ **Active Agent Action**: {message}")

            try:
                with st.spinner("Multi-Agent Discovery & Audit Loop running..."):
                    result = pipeline.run(params, progress_callback=on_progress)
                    st.session_state.search_result = result
                    st.session_state.current_params = params

                progress_container.empty()
                status_container.empty()
                st.success(f"✅ Nova, Max, and Apex discovered & audited {len(result.leads)} qualified leads in {result.duration_seconds}s!")

            except Exception as e:
                progress_container.empty()
                status_container.empty()
                st.error(f"❌ Search Error: {str(e)}")

    # Display Leads Table if results exist
    if st.session_state.search_result:
        res = st.session_state.search_result
        params = st.session_state.current_params

        st.markdown("---")
        st.subheader(f"📊 Qualified Leads for '{params.category}' in {params.area}, {params.city} ({params.country})")
        st.caption(f"🎯 Target Agency Service: **{params.agency_goal}** • Discovered by **Nova**, Audited by **Max**, Pitched by **Apex**")

        if res.warning_message:
            st.warning(f"ℹ️ {res.warning_message}")

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

        col_filter, col_dl1, col_dl2 = st.columns([2, 1.5, 1.5])
        with col_filter:
            score_filter = st.selectbox(
                "Filter by Opportunity Score:",
                options=["All Leads", "HIGH Priority Only", "MEDIUM & HIGH Only"]
            )

        if score_filter == "HIGH Priority Only":
            display_leads = [l for l in res.leads if l.lead_score == "HIGH"]
        elif score_filter == "MEDIUM & HIGH Only":
            display_leads = [l for l in res.leads if l.lead_score in ("HIGH", "MEDIUM")]
        else:
            display_leads = res.leads

        df = leads_to_dataframe(display_leads)

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

        del excel_data, csv_data
        gc.collect()

        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                "Business Name": st.column_config.TextColumn(width="medium"),
                "Phone": st.column_config.TextColumn(width="small"),
                "Lead Score": st.column_config.TextColumn(width="small"),
                "Opportunity": st.column_config.TextColumn(width="medium"),
                "Suggested Service": st.column_config.TextColumn(width="medium"),
                "Pitch Angle": st.column_config.TextColumn(width="large"),
                "Address": st.column_config.TextColumn(width="medium"),
                "Website": st.column_config.LinkColumn(width="medium"),
                "Maps Link": st.column_config.LinkColumn(width="small"),
                "Category": st.column_config.TextColumn(width="small"),
                "Source": st.column_config.TextColumn(width="small")
            },
            hide_index=True
        )
    else:
        st.info("💡 Fill the location and category above, then click **'Launch Multi-Agent Lead & Audit Search'** to scout businesses and generate agency pitches.")


# ========================================================
# TAB 2: AGENCY MULTI-AGENT CHATROOM (ALWAYS ACCESSIBLE!)
# ========================================================
with main_tab2:
    st.markdown("### 💬 Interactive Agency Multi-Agent Chatroom")
    st.caption("Consult your in-house AI agency team anytime! They possess full context of your active search and marketing goals.")

    col_agent_sel, col_agent_desc = st.columns([1, 2])
    with col_agent_sel:
        agent_names = list(AGENT_PROFILES.keys())
        current_agent = st.selectbox(
            "Choose Agent to Chat With:",
            options=agent_names,
            index=agent_names.index(st.session_state.selected_agent)
        )
        st.session_state.selected_agent = current_agent

    profile = AGENT_PROFILES[st.session_state.selected_agent]
    with col_agent_desc:
        st.markdown(f"""
            <div style="background: #1E293B; border: 1px solid #334155; border-radius: 8px; padding: 0.8rem 1rem;">
                <strong>{profile['avatar']} {profile['name']} — {profile['title']}</strong><br/>
                <span style="font-size: 0.85rem; color: #94A3B8;">{profile['description']}</span>
            </div>
        """, unsafe_allow_html=True)
        st.markdown(f'<div style="font-size: 0.85rem; color: #38BDF8; font-weight: 600; margin-top: 0.4rem;">⚡ AI Brain Active: <strong>{llm_helper.get_active_provider_name()}</strong> (Sub-second latency)</div>', unsafe_allow_html=True)

    st.write("")
    st.markdown("##### ⚡ Quick Prompt Starters:")
    quick_cols = st.columns(len(profile["starter_prompts"]))
    selected_quick_prompt = None
    for idx, prompt_text in enumerate(profile["starter_prompts"]):
        with quick_cols[idx]:
            if st.button(prompt_text, key=f"quick_{st.session_state.selected_agent}_{idx}", use_container_width=True):
                selected_quick_prompt = prompt_text

    # Current Context Badge
    active_leads_list = st.session_state.search_result.leads if st.session_state.search_result else []
    active_goal = st.session_state.current_params.agency_goal if st.session_state.current_params else "Website Development"
    active_loc = f"{st.session_state.current_params.area}, {st.session_state.current_params.city}" if st.session_state.current_params else "your target area"

    if active_leads_list:
        st.info(f"📊 **Live Context Attached**: {len(active_leads_list)} leads loaded in {active_loc} (Service Goal: {active_goal})")
    else:
        st.caption("ℹ️ *No leads searched yet. You can still ask any questions on agency strategy, pitch frameworks, pricing, or target niches!*")

    # Display Chat History
    chat_container = st.container()
    with chat_container:
        for chat in st.session_state.chat_history:
            if chat["role"] == "user":
                st.markdown(f'<div class="chat-bubble-user"><strong>You:</strong> {chat["content"]}</div>', unsafe_allow_html=True)
            else:
                agent_p = AGENT_PROFILES.get(chat.get("agent", "Apex"), profile)
                st.markdown(f'<div class="chat-bubble-agent"><strong>{agent_p["avatar"]} {agent_p["name"]} ({agent_p["badge"]}):</strong><br/>{chat["content"]}</div>', unsafe_allow_html=True)

    # Voice Dictation & Whisper Input
    st.write("")
    with st.expander(f"🎙️ Speak with Voice to {profile['name']}", expanded=False):
        voice_prompt = render_voice_input_widget(
            key=f"tab2_voice_{st.session_state.selected_agent}",
            label=f"Tap to record voice prompt for {profile['name']}",
            button_label=f"🚀 Send to {profile['name']}"
        )
        if voice_prompt:
            selected_quick_prompt = voice_prompt

    # Chat Input Box
    user_input = st.chat_input(f"Ask {profile['name']} anything about outreach pitches, lead audits, pricing, or strategy...")

    prompt_to_send = selected_quick_prompt or user_input
    if prompt_to_send:
        st.session_state.chat_history.append({"role": "user", "content": prompt_to_send})

        with st.spinner(f"{profile['name']} is researching businesses & running digital audits..."):
            response = agent_chat_service.respond(
                agent_name=st.session_state.selected_agent,
                user_message=prompt_to_send,
                current_leads=active_leads_list,
                agency_goal=active_goal,
                location_str=active_loc
            )
            # Sync discovered leads to main table and map
            if agent_chat_service.last_discovered_leads:
                st.session_state.search_result = SearchResult(
                    leads=agent_chat_service.last_discovered_leads,
                    total_found=len(agent_chat_service.last_discovered_leads),
                    filtered_count=len(agent_chat_service.last_discovered_leads),
                    duration_seconds=2.0,
                    location_used=None,
                    warning_message=None
                )
                if agent_chat_service.last_params:
                    st.session_state.current_params = agent_chat_service.last_params

            st.session_state.chat_history.append({
                "role": "agent",
                "agent": st.session_state.selected_agent,
                "content": response
            })
            st.rerun()


# ========================================================
# TAB 3: INTERACTIVE GEOGRAPHIC MAP & CLIENT FINDER
# ========================================================
with main_tab3:
    st.markdown("### 🗺️ Interactive Geographic Map & Client Finder")
    st.caption("Click anywhere on the map to drop a pin on a neighborhood, then click 'Scan & Audit Businesses Around Pin' to find and audit clients live!")

    # Determine Map Center
    leads_list = st.session_state.search_result.leads if st.session_state.search_result else []
    leads_with_coords = [l for l in leads_list if l.lat is not None and l.lon is not None]

    default_lat, default_lon = 23.8103, 90.4125 # Default Dhaka
    if st.session_state.marked_location:
        center_lat = st.session_state.marked_location["lat"]
        center_lon = st.session_state.marked_location["lon"]
        map_zoom = 14
    elif leads_with_coords:
        center_lat = sum(l.lat for l in leads_with_coords) / len(leads_with_coords)
        center_lon = sum(l.lon for l in leads_with_coords) / len(leads_with_coords)
        map_zoom = 13
    elif st.session_state.current_params:
        geo = geocode_location(st.session_state.current_params.country, st.session_state.current_params.city, st.session_state.current_params.area)
        if geo:
            center_lat, center_lon = geo.lat, geo.lon
            map_zoom = 13
        else:
            center_lat, center_lon = default_lat, default_lon
            map_zoom = 12
    else:
        center_lat, center_lon = default_lat, default_lon
        map_zoom = 12

    # Choose Map Engine
    col_eng1, col_eng2 = st.columns([2, 1])
    with col_eng1:
        map_engine = st.radio(
            "🗺️ Active Map Engine:",
            options=["🌐 Google Maps (Official JS API + Places Autocomplete)", "🌍 OpenStreetMap (Folium Interactive)"],
            index=0 if GOOGLE_MAPS_API_KEY else 1,
            horizontal=True
        )
    with col_eng2:
        st.caption("⚡ Google Maps JS API enabled with live Places search, interactive click-to-pin, and lead audit popups.")

    if "Google Maps" in map_engine and GOOGLE_MAPS_API_KEY:
        google_html = render_google_map_html(
            api_key=GOOGLE_MAPS_API_KEY,
            center_lat=center_lat,
            center_lon=center_lon,
            zoom=map_zoom,
            leads=leads_with_coords,
            marked_lat=st.session_state.marked_location["lat"] if st.session_state.marked_location else None,
            marked_lon=st.session_state.marked_location["lon"] if st.session_state.marked_location else None,
            radius_km=3.0
        )
        components.html(google_html, height=530)
    else:
        # Build Folium Map
        m = folium.Map(location=[center_lat, center_lon], zoom_start=map_zoom, tiles="CartoDB positron")

        # If user marked a location, plot marked pin and search radius circle
        radius_km_default = 3
        if st.session_state.marked_location:
            m_lat = st.session_state.marked_location["lat"]
            m_lon = st.session_state.marked_location["lon"]
            folium.Marker(
                [m_lat, m_lon],
                tooltip="🎯 Marked Search Target",
                popup="<b>🎯 Your Marked Search Target</b><br/>Ready to scan businesses around this pin.",
                icon=folium.Icon(color="darkred", icon="bullseye", prefix="fa")
            ).add_to(m)
            folium.Circle(
                [m_lat, m_lon],
                radius=radius_km_default * 1000,
                color="#EF4444",
                fill=True,
                fill_color="#EF4444",
                fill_opacity=0.12,
                tooltip=f"{radius_km_default} km Search Radius"
            ).add_to(m)

        # Plot discovered business leads with custom colors & popups
        for lead in leads_with_coords:
            is_high = lead.lead_score == "HIGH"
            has_web = bool(lead.website)
            is_social = any(s in (lead.website or "").lower() for s in ["facebook.com", "instagram.com", "wa.me", "fb.me"])
            
            if is_high or not has_web:
                color = "red"
                icon = "exclamation"
            elif is_social:
                color = "orange"
                icon = "share-alt"
            elif lead.website and lead.website.startswith("http://"):
                color = "blue"
                icon = "lock"
            else:
                color = "green"
                icon = "check"

            digits = re.sub(r"\D", "", lead.phone or "")
            if digits.startswith("01") and len(digits) == 11:
                digits = "880" + digits[1:]
            elif digits.startswith("880"):
                pass
            elif len(digits) == 10 and digits.startswith(("9", "8", "7", "6")):
                digits = "91" + digits

            wa_url = f"https://api.whatsapp.com/send?phone={digits}" if digits else ""

            popup_html = f"""
            <div style="font-family: system-ui, sans-serif; min-width: 220px; max-width: 280px; padding: 2px;">
                <h4 style="margin: 0 0 6px 0; color: #0F172A; font-size: 14px;">🏢 {lead.business_name}</h4>
                <div style="font-size: 12px; margin-bottom: 4px;">
                    <strong>Score:</strong> <span style="color: {'#EF4444' if is_high else '#10B981'}; font-weight: bold;">{lead.lead_score}</span> • <em>{lead.category}</em>
                </div>
                <div style="font-size: 11px; color: #475569; margin-bottom: 4px;"><strong>Audit:</strong> {lead.opportunity_type}</div>
                <div style="font-size: 11px; margin-bottom: 4px;"><strong>Phone:</strong> {lead.phone or '*(None listed)*'}</div>
                <div style="font-size: 11px; margin-bottom: 8px;"><strong>Web:</strong> {'<a href=\"' + lead.website + '\" target=\"_blank\">' + lead.website[:28] + '...</a>' if lead.website else '<span style=\"color:#EF4444;font-weight:bold;\">❌ No Website</span>'}</div>
                <div style="font-size: 11px; background: #F8FAFC; border-left: 2px solid #3B82F6; padding: 4px; margin-bottom: 8px; color: #334155;\">\"{lead.pitch_angle[:110]}...\"</div>
                {f'<a href=\"{wa_url}\" target=\"_blank\" style=\"display:block; text-align:center; background:#25D366; color:white; padding:5px 10px; border-radius:4px; font-weight:bold; font-size:11px; text-decoration:none;\">🟢 Chat on WhatsApp</a>' if wa_url else ''}
            </div>
            """

            folium.Marker(
                [lead.lat, lead.lon],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{lead.business_name} ({lead.lead_score})",
                icon=folium.Icon(color=color, icon=icon, prefix="fa")
            ).add_to(m)

        # Render Map and capture clicks
        map_output = st_folium(
            m,
            width="100%",
            height=520,
            returned_objects=["last_clicked"],
            key="interactive_folium_map"
        )

        # Detect map click to update marked location
        if map_output and map_output.get("last_clicked"):
            click = map_output["last_clicked"]
            last_rec = st.session_state.get("last_recorded_click")
            if not last_rec or (abs(click["lat"] - last_rec.get("lat", 0)) > 0.0001 or abs(click["lng"] - last_rec.get("lng", 0)) > 0.0001):
                st.session_state.last_recorded_click = click
                st.session_state.marked_location = {"lat": click["lat"], "lon": click["lng"]}
                st.rerun()

    # Map Action Controls Card
    st.markdown("---")
    if st.session_state.marked_location:
        m_lat = round(st.session_state.marked_location["lat"], 5)
        m_lon = round(st.session_state.marked_location["lon"], 5)
        
        # Reverse geocode marked coordinates
        loc_display = reverse_geocode(m_lat, m_lon) or f"Coordinates ({m_lat}, {m_lon})"

        st.success(f"📍 **Target Pin Dropped:** `{loc_display}` (Lat: `{m_lat}`, Lon: `{m_lon}`)")

        col_map1, col_map2, col_map3, col_map4 = st.columns([2, 1.5, 1, 1.5])
        with col_map1:
            map_cat = st.selectbox(
                "Niche to Scan:",
                options=["Gym", "Gymnastics", "Dental Clinic", "Clinic & Healthcare", "Restaurant & Cafe", "Beauty Salon & Spa", "Car Repair", "Real Estate Agency", "Custom"],
                key="map_scan_niche"
            )
            if map_cat == "Custom":
                map_cat = st.text_input("Custom Niche", value="Gym", key="custom_map_niche")
        with col_map2:
            map_goal = st.selectbox(
                "Agency Service Pitch:",
                options=["Website Development", "AI Automation / Chatbots", "Local SEO / Google Maps", "General B2B Outreach"],
                key="map_scan_goal"
            )
        with col_map3:
            map_radius = st.selectbox("Radius", options=["2 km", "3 km", "5 km"], index=1, key="map_scan_radius")
            radius_km_val = int(map_radius.split()[0])
        with col_map4:
            st.write("")
            st.write("")
            scan_pin_btn = st.button("🚀 Scan Around Pin", use_container_width=True, type="primary")

        if scan_pin_btn:
            with st.spinner(f"Nova, Max & Apex scanning {map_cat} around {loc_display}..."):
                # Compute radial bounding box
                radial_bbox = create_radial_bbox(m_lat, m_lon, radius_km=radius_km_val)
                
                # Use Tavily Search Provider if available, else OSM
                from src.providers.tavily_provider import TavilySearchProvider
                from src.providers.osm_provider import OpenStreetMapProvider
                from src.services.website_auditor import website_auditor

                leads_found = []
                if TAVILY_API_KEY:
                    try:
                        tavily = TavilySearchProvider(TAVILY_API_KEY)
                        leads_found = tavily.discover_businesses(
                            category=map_cat,
                            location_str=loc_display,
                            limit=20,
                            center_lat=m_lat,
                            center_lon=m_lon
                        )
                    except Exception:
                        leads_found = []

                if not leads_found:
                    try:
                        osm = OpenStreetMapProvider()
                        leads_found = osm.search(bbox=radial_bbox, category=map_cat, max_results=20, location_name=loc_display)
                    except Exception:
                        leads_found = []

                # Live website audit
                for l in leads_found:
                    audit = website_auditor.audit(l.business_name, l.website, l.phone, map_cat, loc_display, agency_goal=map_goal)
                    l.lead_score = audit.get("opportunity_score", l.lead_score)
                    l.opportunity_type = audit.get("badge", l.opportunity_type)
                    l.suggested_service = audit.get("suggested_service", map_goal)
                    l.pitch_angle = audit.get("pitch_hook", l.pitch_angle)

                if leads_found:
                    st.session_state.search_result = SearchResult(
                        leads=leads_found,
                        total_found=len(leads_found),
                        filtered_count=len(leads_found),
                        duration_seconds=2.4,
                        location_used=None,
                        warning_message=None
                    )
                    st.session_state.current_params = SearchParams(
                        country="Bangladesh",
                        city=loc_display.split(",")[-2].strip() if "," in loc_display else "Dhaka",
                        area=loc_display.split(",")[0].strip(),
                        category=map_cat,
                        limit=len(leads_found),
                        agency_goal=map_goal
                    )
                    st.session_state.chat_history.append({
                        "role": "agent",
                        "agent": "Nova",
                        "content": f"🔭 **Nova (Scout) & 🔍 Max (Auditor):** Successfully discovered and audited **{len(leads_found)} {map_cat} leads** around your marked pin in **{loc_display}**! Pins are displayed on your map and loaded into the Leads Table for instant Excel/CSV download."
                    })
                    st.success(f"✅ Discovered & Audited {len(leads_found)} businesses! Pins updated on map and synchronized to Leads Table.")
                    st.rerun()
                else:
                    st.warning(f"No {map_cat} businesses found within {map_radius} of this pin. Try selecting an adjacent neighborhood or a broader niche.")
    else:
        st.info("💡 **How to pick a location:** Simply **click anywhere on the map above** to drop a search pin on any neighborhood or street, then scan all local businesses around that exact spot!")
