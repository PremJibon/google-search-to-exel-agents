import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models import SearchParams
from src.pipelines.lead_pipeline import LeadPipeline

def test_pipeline_kushtia():
    print("--- Running Test: Bangladesh / Kushtia / Gyms ---")
    pipeline = LeadPipeline()
    params = SearchParams(
        country="Bangladesh",
        city="Kushtia",
        area="Kushtia Sadar",
        category="Gyms",
        limit=10,
        require_phone=False
    )

    def progress(pct, msg):
        print(f"[{pct}%] {msg}")

    result = pipeline.run(params, progress_callback=progress)
    print(f"Discovered: {result.total_found}, Filtered: {result.filtered_count}")
    print(f"Duration: {result.duration_seconds}s")
    if result.warning_message:
        print(f"Warning/Guidance: {result.warning_message}")
    for lead in result.leads:
        print(f"- {lead.business_name} | {lead.address} | {lead.maps_link}")

if __name__ == "__main__":
    test_pipeline_kushtia()
