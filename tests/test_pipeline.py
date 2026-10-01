import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models import SearchParams
from src.pipelines.lead_pipeline import LeadPipeline
from src.services.exporter import export_to_excel, export_to_csv

def test_pipeline_bangalore():
    print("--- Running Test: Bangalore / Koramangala / Restaurants ---")
    pipeline = LeadPipeline()
    params = SearchParams(
        country="India",
        city="Bangalore",
        area="Koramangala",
        category="Restaurants",
        limit=10,
        require_phone=False
    )

    def progress(pct, msg):
        print(f"[{pct}%] {msg}")

    result = pipeline.run(params, progress_callback=progress)
    print(f"Discovered: {result.total_found} leads, Filtered count: {result.filtered_count}")
    print(f"Time taken: {result.duration_seconds}s")

    for i, lead in enumerate(result.leads[:5], 1):
        print(f"{i}. {lead.business_name} | Phone: {lead.phone or 'None'} | Address: {lead.address[:30]}... | Maps: {lead.maps_link}")

    # Test exporter
    xlsx_bytes = export_to_excel(result.leads)
    csv_bytes = export_to_csv(result.leads)
    print(f"Excel bytes generated: {len(xlsx_bytes)} bytes")
    print(f"CSV bytes generated: {len(csv_bytes)} bytes")
    assert len(xlsx_bytes) > 0, "Excel output is empty"
    assert len(csv_bytes) > 0, "CSV output is empty"
    print("SUCCESS: Pipeline & Exporters verified!")

if __name__ == "__main__":
    test_pipeline_bangalore()
