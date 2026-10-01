import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models import SearchParams
from src.pipelines.lead_pipeline import LeadPipeline
from src.services.exporter import export_to_excel

def test_agency_qualification():
    print("--- Testing Two-Agent Pipeline: Website Sales Outreach ---")
    pipeline = LeadPipeline()
    params = SearchParams(
        country="India",
        city="Bangalore",
        area="Koramangala",
        category="Dental clinics",
        limit=5,
        agency_goal="Website Development"
    )

    result = pipeline.run(params)
    print(f"Total Found: {result.total_found}, Qualified Leads: {len(result.leads)}")

    for i, lead in enumerate(result.leads, 1):
        print(f"\nLead #{i}: {lead.business_name}")
        print(f"  Score: {lead.lead_score} | Opportunity: {lead.opportunity_type}")
        print(f"  Service: {lead.suggested_service}")
        print(f"  Pitch: {lead.pitch_angle[:100]}...")

    excel_bytes = export_to_excel(result.leads)
    assert len(excel_bytes) > 0
    print("\nSUCCESS: Two-Agent Agency Qualification verified!")

if __name__ == "__main__":
    test_agency_qualification()
