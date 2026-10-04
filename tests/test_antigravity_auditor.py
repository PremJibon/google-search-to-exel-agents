import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from src.services.website_auditor import website_auditor
from src.services.normalizer import generate_whatsapp_link
from src.models import Lead, SearchParams
from src.services.exporter import export_to_excel, export_to_csv

def test_antigravity_audit_suite():
    print("==================================================")
    print("RUNNING ANTIGRAVITY WEBSITE AUDITOR TEST SUITE")
    print("==================================================")

    # 1. Test No Website
    print("\n[TEST 1] Auditing Business With NO Website...")
    r1 = website_auditor.audit("Elite Dental Care", "", phone="01711223344", location="Dhaka, Bangladesh")
    assert r1["has_website"] is False
    assert r1["status"] == "NO_WEBSITE"
    assert r1["audit_score"] <= 15, f"Expected critical score <= 15, got {r1['audit_score']}"
    assert r1["opportunity_score"] == "HIGH"
    assert len(r1["flaws"]) >= 3
    print(f"-> PASSED: No-website detected with Health Score: {r1['audit_score']}/100 and Opportunity: {r1['opportunity_score']}")
    print(f"   Pitch: {r1['pitch_hook'][:80]}...")

    # 2. Test Social Media Only
    print("\n[TEST 2] Auditing Business With Social Media Link Only...")
    r2 = website_auditor.audit("FitZone Gym", "https://www.facebook.com/fitzonebd", phone="+8801812345678", location="Dhaka")
    assert r2["has_website"] is False
    assert r2["status"] == "SOCIAL_ONLY"
    assert r2["audit_score"] <= 35, f"Expected poor score <= 35, got {r2['audit_score']}"
    assert r2["opportunity_score"] == "HIGH"
    print(f"-> PASSED: Social-only profile detected with Health Score: {r2['audit_score']}/100")

    # 3. Test Live Website (Fast Mock or Real Site)
    print("\n[TEST 3] Auditing Live Website...")
    r3 = website_auditor.audit("Google Search", "https://google.com", phone="+1234567890", location="Global")
    assert r3["has_website"] is True
    assert r3["status"] == "LIVE_WEBSITE"
    assert r3["audit_score"] >= 30, f"Expected live website score >= 30, got {r3['audit_score']}"
    print(f"-> PASSED: Live site audited with Health Score: {r3['audit_score']}/100, Badge: {r3['badge']}")

    # 4. Test WhatsApp Link Generation
    print("\n[TEST 4] Testing WhatsApp Link Normalization...")
    wa1 = generate_whatsapp_link("01712345678", country="Bangladesh")
    assert wa1 == "https://wa.me/8801712345678", f"Unexpected WA link: {wa1}"
    wa2 = generate_whatsapp_link("+91 98765 43210", country="India")
    assert wa2 == "https://wa.me/919876543210", f"Unexpected WA link: {wa2}"
    print(f"-> PASSED: WhatsApp links normalized correctly: {wa1} and {wa2}")

    # 5. Test Full Lead & Exporter Integration
    print("\n[TEST 5] Testing Excel and CSV Exporter with Antigravity Fields...")
    lead = Lead(
        business_name="Apex Dental Clinic",
        phone="01711223344",
        whatsapp_link=wa1,
        address="Dhanmondi, Dhaka",
        website="https://facebook.com/apexdental",
        maps_link="https://maps.google.com/?q=Apex+Dental",
        category="Dental Clinic",
        source="Google Search & Maps",
        lead_score=r2["opportunity_score"],
        audit_score=r2["audit_score"],
        opportunity_type=r2["badge"],
        suggested_service=r2["suggested_service"],
        pitch_angle=r2["pitch_hook"],
        audit_flaws=r2["top_flaws"]
    )

    xlsx_bytes = export_to_excel([lead])
    csv_bytes = export_to_csv([lead])
    assert len(xlsx_bytes) > 0, "Excel output empty"
    assert len(csv_bytes) > 0, "CSV output empty"
    csv_str = csv_bytes.decode("utf-8-sig")
    assert "WhatsApp Link" in csv_str
    assert "Audit Score" in csv_str
    assert "Tailored Pitch Angle" in csv_str
    assert "Audit Flaws" in csv_str
    print(f"-> PASSED: Exported {len(xlsx_bytes)} bytes Excel & {len(csv_bytes)} bytes CSV with all Antigravity fields!")

    print("\n==================================================")
    print("ALL ANTIGRAVITY AUDITOR & EXPORT TESTS PASSED 100%!")
    print("==================================================")

if __name__ == "__main__":
    test_antigravity_audit_suite()
