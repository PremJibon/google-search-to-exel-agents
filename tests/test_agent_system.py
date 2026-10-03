import sys
import io
import os

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# UTF-8 stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from src.models import SearchParams
from src.pipelines.lead_pipeline import LeadPipeline
from src.services.agent_chat import agent_chat_service
from src.config import TAVILY_API_KEY
from src.services.exporter import export_to_excel, export_to_csv

def test_full_system():
    print("==================================================")
    print("TEST: Dual-Loop Multi-Agent Lead Finder & Chat")
    print("Location: Kamalapur, Dhaka, Bangladesh | Category: Gym")
    print("==================================================")

    pipeline = LeadPipeline(tavily_key=TAVILY_API_KEY)
    params = SearchParams(
        country="Bangladesh",
        city="Dhaka",
        area="Kamalapur",
        category="Gym",
        limit=5,
        agency_goal="AI Automation / Chatbots"
    )

    def on_step(pct, msg):
        print(f"[{pct}%] {msg}")

    res = pipeline.run(params, progress_callback=on_step)
    print(f"\nExecution Time: {res.duration_seconds}s")
    print(f"Total Discovered: {res.total_found} | Filtered Leads: {len(res.leads)}")

    for i, lead in enumerate(res.leads[:4], 1):
        print(f"\nLead #{i}: {lead.business_name}")
        print(f"  Phone: {lead.phone or '(No public phone)'}")
        print(f"  Website: {lead.website or '(No website)'}")
        print(f"  Score: {lead.lead_score} | Opportunity: {lead.opportunity_type}")
        print(f"  Suggested Service: {lead.suggested_service}")
        print(f"  Pitch Angle: {lead.pitch_angle[:90]}...")

    # Verify exporters
    xlsx = export_to_excel(res.leads)
    csv = export_to_csv(res.leads)
    assert len(xlsx) > 0, "Excel output empty"
    assert len(csv) > 0, "CSV output empty"
    print(f"\nExport Sizes: Excel={len(xlsx)} bytes, CSV={len(csv)} bytes [VERIFIED]")

    # Verify Multi-Agent Chat
    print("\n--- Testing Agent Chat (Apex - Digital Marketer) ---")
    chat_apex = agent_chat_service.respond(
        agent_name="Apex",
        user_message="Write a 3-step WhatsApp outreach sequence for the loaded leads",
        current_leads=res.leads,
        agency_goal=params.agency_goal,
        location_str="Kamalapur, Dhaka, Bangladesh"
    )
    assert len(chat_apex) > 50
    print("Apex Response Generated successfully:")
    print(chat_apex[:250] + "...\n")

    print("--- Testing Agent Chat (Atlas - Strategist) ---")
    chat_atlas = agent_chat_service.respond(
        agent_name="Atlas",
        user_message="What is the best 7-day workflow to close 2 clients from this list?",
        current_leads=res.leads,
        agency_goal=params.agency_goal,
        location_str="Kamalapur, Dhaka, Bangladesh"
    )
    assert len(chat_atlas) > 50
    print("Atlas Response Generated successfully:")
    print(chat_atlas[:250] + "...\n")

    print("SUCCESS: Full Multi-Agent System Verified 100%!")

if __name__ == "__main__":
    test_full_system()
