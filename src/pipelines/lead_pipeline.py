import time
from typing import Callable, Optional
from src.models import SearchParams, SearchResult, Lead
from src.providers.base import BusinessDataProvider
from src.providers.osm_provider import OpenStreetMapProvider
from src.services.geocoding import geocode_location
from src.services.deduplicator import deduplicate_leads
from src.services.agency_qualifier import qualify_leads_batch

class LeadPipeline:
    """
    Central multi-agent pipeline orchestrator driving:
    1. Nova (Scout): Geocodes & discovers local business listings
    2. Nova: Deduplicates and applies initial boundary filters
    3. Max (Auditor): Audits digital assets & flags high-priority prospects needing websites/booking
    4. Nova & Max Handshake: Immediately runs Deep Web Search (Tavily/Serper) to uncover missing websites & phones
    5. Apex (Marketer): Generates tailored outreach pitches & conversion angles
    """

    def __init__(self, provider: Optional[BusinessDataProvider] = None, tavily_key: Optional[str] = None):
        self.provider = provider or OpenStreetMapProvider()
        self.tavily_key = (tavily_key or "").strip()

    def run(
        self,
        params: SearchParams,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> SearchResult:
        start_time = time.time()

        def update(pct: int, msg: str):
            if progress_callback:
                progress_callback(pct, msg)

        # Enforce memory safety clamp (512MB RAM limit)
        from src.services.security import clamp_lead_limit
        safe_limit = clamp_lead_limit(params.limit, max_cap=100)

        # 1. Geocoding by Nova
        update(15, f"[Nova - Scout] Geocoding target area: {params.area}, {params.city}, {params.country}...")
        location = geocode_location(params.country, params.city, params.area)

        if not location:
            raise ValueError(
                f"Could not locate '{params.area}' in '{params.city}, {params.country}'. "
                "Try checking spelling or choosing a neighboring area."
            )

        # 2. Querying Business POIs
        update(35, f"[Nova - Scout] Scanning businesses ({params.category}) via {self.provider.name}...")
        raw_leads = []
        try:
            raw_leads = self.provider.search(
                bbox=location.bounding_box,
                category=params.category,
                keyword=params.keyword,
                max_results=safe_limit,
                progress_callback=progress_callback,
                location_name=f"{params.area}, {params.city}, {params.country}"
            )
        except Exception:
            raw_leads = []

        # Automatic Intelligent Fallback: If primary provider returned 0 leads and Tavily is available
        if not raw_leads and self.tavily_key:
            try:
                update(45, f"[Nova - Scout] Zero listings found in {self.provider.name}; activating Tavily Deep Web Discovery...")
                from src.providers.tavily_provider import TavilySearchProvider
                tavily_fallback = TavilySearchProvider(self.tavily_key)
                if tavily_fallback.is_available:
                    raw_leads = tavily_fallback.discover_businesses(
                        category=params.category,
                        location_str=f"{params.area}, {params.city}, {params.country}",
                        limit=safe_limit,
                        keyword=params.keyword,
                        center_lat=location.lat,
                        center_lon=location.lon,
                        progress_callback=progress_callback
                    )
            except Exception:
                pass

        total_raw_found = len(raw_leads)

        # 3. Deduplication
        update(60, f"[Nova - Scout] Deduplicating {total_raw_found} discovered commercial records...")
        unique_leads = deduplicate_leads(raw_leads)

        # 4. Filter Enforcement
        filtered_leads = []
        for lead in unique_leads:
            if params.require_phone and not lead.phone:
                continue
            if params.require_website and not lead.website:
                continue
            filtered_leads.append(lead)
            if len(filtered_leads) >= safe_limit:
                break

        # 5. Agent 2 (Max): Initial Digital Audit
        update(75, f"[Max - Auditor] Auditing {len(filtered_leads)} leads for '{params.agency_goal}' opportunities...")
        from src.services.website_auditor import website_auditor
        for l in filtered_leads:
            audit = website_auditor.audit(l.business_name, l.website, l.phone, params.category, f"{params.area}, {params.city}")
            l.lead_score = audit.get("opportunity_score", l.lead_score)
            l.opportunity_type = audit.get("badge", l.opportunity_type)
            l.suggested_service = audit.get("suggested_service", l.suggested_service)
            l.pitch_angle = audit.get("pitch_hook", l.pitch_angle)

        # 6. Collaborative Handshake: Nova & Max Deep Search Loop
        # When Max finds businesses needing a website or contact number, Nova immediately searches for them
        if self.tavily_key:
            try:
                from src.providers.tavily_provider import TavilySearchProvider
                tavily = TavilySearchProvider(self.tavily_key)
                if tavily.is_available:
                    # Target leads that have HIGH priority or missing contact info
                    candidates = [l for l in filtered_leads if (not l.website or not l.phone)][:4]
                    if candidates:
                        update(85, f"[Nova & Max Co-Pilot] Immediately running Deep Search for {len(candidates)} high-priority businesses...")
                        for candidate in candidates:
                            info = tavily.search_business_info(candidate.business_name, params.city, params.country)
                            if info:
                                if not candidate.website and info.get("url"):
                                    candidate.website = info["url"]
                                if not candidate.phone and info.get("phone"):
                                    candidate.phone = info["phone"]
                        # Re-audit enriched leads
                        for candidate in candidates:
                            audit = website_auditor.audit(candidate.business_name, candidate.website, candidate.phone, params.category, f"{params.area}, {params.city}")
                            candidate.lead_score = audit.get("opportunity_score", candidate.lead_score)
                            candidate.opportunity_type = audit.get("badge", candidate.opportunity_type)
                            candidate.suggested_service = audit.get("suggested_service", candidate.suggested_service)
                            candidate.pitch_angle = audit.get("pitch_hook", candidate.pitch_angle)
            except Exception:
                pass

        # 7. Agent 3 (Apex): Custom Marketing Angle Synthesis
        update(95, f"[Apex - Marketer] Crafting bespoke cold outreach pitch angles for {params.agency_goal}...")

        # Guidance checks
        warning_msg = None
        if total_raw_found > 0 and len(filtered_leads) == 0:
            if params.require_phone:
                warning_msg = (
                    f"Found {total_raw_found} businesses matching '{params.category}', "
                    "but none had public phone numbers listed in OpenStreetMap. "
                    "Uncheck 'Require Phone Number' to see all businesses with addresses, or enable Deep Search."
                )
            elif params.require_website:
                warning_msg = (
                    f"Found {total_raw_found} businesses matching '{params.category}', but they do NOT have websites! "
                    "Since your agency goal is selling Websites, these businesses are your #1 prime prospects. "
                    "Uncheck 'Require Website' to view and pitch them."
                )
        elif total_raw_found == 0:
            warning_msg = (
                f"No businesses found matching '{params.category}' in this boundary. "
                "Try searching for a related category (e.g. 'Gym', 'Fitness', 'Clinic') or selecting a point on the 'Geographic Map' tab."
            )

        duration = round(time.time() - start_time, 2)
        update(100, f"Completed in {duration}s! Ready for export.")

        return SearchResult(
            leads=filtered_leads,
            total_found=total_raw_found,
            filtered_count=len(filtered_leads),
            duration_seconds=duration,
            location_used=location,
            warning_message=warning_msg
        )
