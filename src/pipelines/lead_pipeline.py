import time
from typing import Callable, Optional
from src.models import SearchParams, SearchResult, Lead
from src.providers.base import BusinessDataProvider
from src.providers.osm_provider import OpenStreetMapProvider
from src.services.geocoding import geocode_location
from src.services.deduplicator import deduplicate_leads

class LeadPipeline:
    """
    Central pipeline orchestrator that drives:
    Input Validation -> Geocoding -> POI Querying -> Normalization -> Deduplication -> Filtering -> Result Set.
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

        # 1. Geocoding
        update(15, f"Geocoding target area: {params.area}, {params.city}...")
        location = geocode_location(params.country, params.city, params.area)

        if not location:
            raise ValueError(
                f"Could not locate '{params.area}' in '{params.city}, {params.country}'. "
                "Try checking the spelling or using a broader city name."
            )

        # 2. Querying Business POIs
        update(40, f"Querying businesses ({params.category}) from {self.provider.name}...")
        raw_leads = self.provider.search(
            bbox=location.bounding_box,
            category=params.category,
            keyword=params.keyword,
            max_results=params.limit,
            progress_callback=progress_callback,
            location_name=f"{params.area}, {params.city}, {params.country}"
        )

        total_raw_found = len(raw_leads)

        # 3. Deduplication
        update(70, f"[Agent 1: Discovery] Deduplicating {total_raw_found} discovered records...")
        unique_leads = deduplicate_leads(raw_leads)

        # 4. Strict Filtering
        update(80, "[Agent 1: Discovery] Applying contact filters...")
        filtered_leads = []
        for lead in unique_leads:
            if params.require_phone and not lead.phone:
                continue
            if params.require_website and not lead.website:
                continue
            filtered_leads.append(lead)
            if len(filtered_leads) >= params.limit:
                break

        # 5. Agent 2: Agency Qualification & Opportunity Audit
        update(90, f"[Agent 2: Auditor] Auditing leads for '{params.agency_goal}' opportunities & pitch angles...")
        from src.services.agency_qualifier import qualify_leads_batch
        qualify_leads_batch(filtered_leads, params.agency_goal)

        # Optional Tavily Web Footprint Intelligence
        if self.tavily_key:
            try:
                from src.providers.tavily_provider import TavilySearchProvider
                tavily = TavilySearchProvider(self.tavily_key)
                if tavily.is_available:
                    update(95, "[Agent 2: Auditor] Verifying web footprints via Tavily API...")
                    for lead in filtered_leads[:3]:
                        if not lead.website:
                            info = tavily.search_business_info(lead.business_name, params.city)
                            if info and info.get("url"):
                                lead.website = info["url"]
                                qualify_leads_batch([lead], params.agency_goal)
            except Exception:
                pass

        # 5. Warning / Guidance Checks
        warning_msg = None
        if total_raw_found > 0 and len(filtered_leads) == 0:
            if params.require_phone:
                warning_msg = (
                    f"Found {total_raw_found} businesses matching '{params.category}', "
                    "but none had public phone numbers listed in OpenStreetMap. "
                    "Uncheck 'Require Phone Number' to see all businesses with addresses and maps links."
                )
            elif params.require_website:
                warning_msg = (
                    f"Found {total_raw_found} businesses, but none had websites listed. "
                    "Try unchecking 'Require Website'."
                )
        elif total_raw_found == 0:
            warning_msg = (
                f"No businesses found matching '{params.category}' in this boundary. "
                "Try searching for a broader category (e.g. 'Restaurant', 'Clinic', 'Shop') or broader area."
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
