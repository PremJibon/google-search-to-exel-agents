import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models import SearchParams
from src.providers.serper_provider import SerperGoogleMapsProvider
from src.pipelines.lead_pipeline import LeadPipeline
from src.services.exporter import export_to_excel, export_to_csv
from src.config import SERPER_API_KEY

def test_serper_provider():
    print("==================================================")
    print("TEST: Serper Google Maps Provider")
    print(f"SERPER_API_KEY loaded: {'YES' if SERPER_API_KEY else 'NO (Empty)'}")
    print("==================================================")

    if not SERPER_API_KEY:
        print("[INFO] SERPER_API_KEY is currently empty in .env.")
        print("[INFO] Demonstrating mock/fallback resilience when key is not yet set.")
        try:
            provider = SerperGoogleMapsProvider(api_key="")
            pipeline = LeadPipeline(provider=provider)
            params = SearchParams(
                country="India",
                city="Bangalore",
                area="Koramangala",
                category="Restaurants",
                limit=5
            )
            pipeline.run(params)
        except ValueError as e:
            print(f"[EXPECTED GUARD] Clean error raised when key is missing: {e}")
            print("SUCCESS: Missing key guard verified!")
            return

    # If key is provided:
    provider = SerperGoogleMapsProvider(api_key=SERPER_API_KEY)
    pipeline = LeadPipeline(provider=provider)
    params = SearchParams(
        country="India",
        city="Bangalore",
        area="Koramangala",
        category="Restaurants",
        limit=5,
        agency_goal="Website Development"
    )

    def progress(pct, msg):
        print(f"[{pct}%] {msg}")

    result = pipeline.run(params, progress_callback=progress)
    print(f"\nDiscovered: {result.total_found} leads via Google Maps (Serper) in {result.duration_seconds}s")
    for i, lead in enumerate(result.leads[:5], 1):
        print(f"{i}. {lead.business_name} | Phone: {lead.phone} | Addr: {lead.address[:30]} | Maps: {lead.maps_link}")
        print(f"   Score: {lead.lead_score} | Service: {lead.suggested_service}")
        print(f"   Pitch: {lead.pitch_angle[:80]}...")

    xlsx = export_to_excel(result.leads)
    csv = export_to_csv(result.leads)
    print(f"Excel Export Size: {len(xlsx)} bytes")
    print(f"CSV Export Size: {len(csv)} bytes")
    assert len(xlsx) > 0
    assert len(csv) > 0
    print("SUCCESS: Google Maps via Serper verified!")

if __name__ == "__main__":
    test_serper_provider()
