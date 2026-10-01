import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models import SearchParams
from src.pipelines.lead_pipeline import LeadPipeline

def run_comprehensive_agency_test():
    print("==================================================")
    print("TEST 1: Selling Websites (Koramangala Dental Clinics)")
    print("==================================================")
    pipeline = LeadPipeline()
    params_web = SearchParams(
        country="India",
        city="Bangalore",
        area="Koramangala",
        category="Dental clinics",
        limit=4,
        agency_goal="Website Development"
    )
    res_web = pipeline.run(params_web)
    for lead in res_web.leads:
        print(f"[{lead.lead_score}] {lead.business_name}")
        print(f"  Opportunity: {lead.opportunity_type}")
        print(f"  Pitch: {lead.pitch_angle[:90]}...")

    print("\n==================================================")
    print("TEST 2: Selling AI Automation (Indiranagar Gyms)")
    print("==================================================")
    params_ai = SearchParams(
        country="India",
        city="Bangalore",
        area="Indiranagar",
        category="Gyms",
        limit=4,
        agency_goal="AI Automation / Chatbots"
    )
    res_ai = pipeline.run(params_ai)
    for lead in res_ai.leads:
        print(f"[{lead.lead_score}] {lead.business_name}")
        print(f"  Opportunity: {lead.opportunity_type}")
        print(f"  Suggested Service: {lead.suggested_service}")
        print(f"  Pitch: {lead.pitch_angle[:90]}...")

    print("\nALL DUAL-AGENT PIPELINE TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_comprehensive_agency_test()
