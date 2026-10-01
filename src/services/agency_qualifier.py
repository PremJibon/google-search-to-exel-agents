from typing import List, Optional
from src.models import Lead

HIGH_INQUIRY_CATEGORIES = {
    "dental clinic", "dentist", "doctor", "clinic", "hospital",
    "gym", "fitness", "yoga", "spa", "salon", "beauty", "hairdresser",
    "car repair", "car wash", "real estate", "lawyer", "hotel", "restaurant"
}

def qualify_lead_for_agency(lead: Lead, agency_goal: str) -> Lead:
    """
    Agent 2 (Qualification & Opportunity Checker):
    Audits a discovered lead and assigns an opportunity score, service recommendation,
    and tailored cold pitch angle according to the agency's business goal.
    """
    web = (lead.website or "").lower().strip()
    phone = (lead.phone or "").strip()
    cat = (lead.category or "").lower().strip()

    if agency_goal == "Website Development":
        if not web:
            lead.lead_score = "HIGH"
            lead.opportunity_type = "No Official Website"
            lead.suggested_service = "Custom Responsive Website"
            lead.pitch_angle = (
                f"Hi {lead.business_name}, I noticed you don't have an official website listed on Google Maps. "
                "Local customers searching for services in your area are clicking on competitors with active sites. "
                "We can build you a high-converting website with mobile booking in 5 days."
            )
        elif any(social in web for social in ["facebook.com", "instagram.com", "fb.me", "wa.me"]):
            lead.lead_score = "HIGH"
            lead.opportunity_type = "Social Media Only (No Dedicated Site)"
            lead.suggested_service = "Dedicated Business Website"
            lead.pitch_angle = (
                f"Hi {lead.business_name}, you're currently using social media as your primary link. "
                "A dedicated website with local SEO can double your search visibility and allow direct lead capture."
            )
        elif web.startswith("http://"):
            lead.lead_score = "MEDIUM"
            lead.opportunity_type = "Insecure Website (HTTP)"
            lead.suggested_service = "SSL Security & Redesign"
            lead.pitch_angle = (
                f"Hi {lead.business_name}, your website is flagged as Not Secure in browsers. "
                "We can upgrade your security, speed, and design to protect customer trust."
            )
        else:
            lead.lead_score = "LOW"
            lead.opportunity_type = "Existing Website"
            lead.suggested_service = "Conversion & Speed Redesign"
            lead.pitch_angle = (
                f"Hi {lead.business_name}, we ran a performance check on your site. "
                "We can improve your mobile loading speed and add automated lead forms."
            )

    elif agency_goal == "AI Automation / Chatbots":
        is_high_inquiry = any(k in cat for k in HIGH_INQUIRY_CATEGORIES)
        
        if is_high_inquiry and phone:
            lead.lead_score = "HIGH"
            lead.opportunity_type = "High-Volume Call & Booking Need"
            lead.suggested_service = "24/7 AI Receptionist & WhatsApp Bot"
            lead.pitch_angle = (
                f"Hi {lead.business_name}, how many appointment calls or inquiries does your team miss during peak hours? "
                "We implement an AI receptionist that handles inquiries, books appointments 24/7, and syncs directly to your calendar."
            )
        elif is_high_inquiry:
            lead.lead_score = "HIGH"
            lead.opportunity_type = "Inquiry Capture Needed"
            lead.suggested_service = "AI Website Chatbot & Lead Responder"
            lead.pitch_angle = (
                f"Hi {lead.business_name}, we can install a smart AI chatbot on your site to answer FAQs, "
                "qualify customer inquiries, and send instant notifications to your sales team."
            )
        else:
            lead.lead_score = "MEDIUM"
            lead.opportunity_type = "Business Workflow Automation"
            lead.suggested_service = "CRM & Follow-up Automation"
            lead.pitch_angle = (
                f"Hi {lead.business_name}, we automate repetitive customer follow-ups and invoicing "
                "to save your team 10+ hours every week."
            )

    else:  # General B2B Prospecting / Local SEO
        if phone and web:
            lead.lead_score = "HIGH"
            lead.opportunity_type = "Complete Contact Profile"
            lead.suggested_service = "Direct B2B Outreach"
            lead.pitch_angle = f"Verified lead with active phone ({phone}) and website ready for cold outreach."
        elif phone:
            lead.lead_score = "HIGH"
            lead.opportunity_type = "Direct Phone Verified"
            lead.suggested_service = "Cold Calling / WhatsApp"
            lead.pitch_angle = f"Phone contact ready for direct phone outreach: {phone}."
        else:
            lead.lead_score = "LOW"
            lead.opportunity_type = "Incomplete Profile"
            lead.suggested_service = "Profile Enrichment"
            lead.pitch_angle = "Needs manual phone lookup before sales contact."

    return lead

def qualify_leads_batch(leads: List[Lead], agency_goal: str) -> List[Lead]:
    """Applies Agent 2 qualification audit to a batch of leads."""
    for lead in leads:
        qualify_lead_for_agency(lead, agency_goal)
    return leads
