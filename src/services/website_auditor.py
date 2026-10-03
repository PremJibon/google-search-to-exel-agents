import re
import time
import requests
from typing import Dict, Any, Optional
from src.services.normalizer import sanitize_url, sanitize_phone

class WebsiteAuditor:
    """
    Automated real-time website and digital footprint auditor.
    Inspects business websites across 7 Agency Service Modes:
    1. Website Development
    2. AI Automation / Chatbots
    3. Local SEO / Google Maps
    4. Review & Reputation Management
    5. Social Media & Content Marketing
    6. Paid Ads & Lead Generation
    7. General B2B Prospecting
    """

    def __init__(self, request_timeout: float = 3.5):
        self.request_timeout = request_timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 LeadAuditor/2.1"
        }

    def audit(
        self,
        business_name: str,
        website: str,
        phone: str = "",
        category: str = "",
        location: str = "",
        agency_goal: str = "Website Development"
    ) -> Dict[str, Any]:
        """
        Executes a real-time audit on a business's website or flags missing web presence
        tailored to the agency's specific target service.
        """
        clean_url = sanitize_url(website) if website else ""
        clean_ph = sanitize_phone(phone) if phone else ""
        cat_display = category.title() if category else "Local Business"
        loc_display = location if location else "your area"

        # ========================================================
        # CASE A: NO WEBSITE LISTED
        # ========================================================
        if not clean_url:
            if "ai automation" in agency_goal.lower() or "chatbot" in agency_goal.lower():
                service = "AI WhatsApp Receptionist & Instant Mobile Site"
                pricing = "$600 – $1,500 setup"
                pitch = (
                    f"Hi {business_name}, I noticed your business doesn't have an official online portal in {loc_display}. "
                    "You're missing high-intent customers who search online. "
                    "We can set up a 24/7 AI receptionist on WhatsApp and a fast mobile page to capture and book customers automatically."
                )
            elif "seo" in agency_goal.lower():
                service = "Google Maps Local Pack Ranking & Business Website"
                pricing = "$500 setup + $400/mo"
                pitch = (
                    f"Hi {business_name}, without an official website linked to your Google listing, your business is losing the top 3 map pack positions to competitors. "
                    "We can build you a local-SEO optimized website to put you on top of Google Maps."
                )
            else:
                service = "Custom High-Converting Mobile Website & Local SEO"
                pricing = "$500 – $1,200"
                pitch = (
                    f"Hi {business_name}, I noticed you don't have an official website listed on Google Maps in {loc_display}. "
                    "When customers search on mobile, they are clicking on competitor sites. "
                    "We can build you a fast, modern website with WhatsApp instant booking in just 5 days."
                )

            return {
                "has_website": False,
                "status": "NO_WEBSITE",
                "opportunity_score": "HIGH",
                "badge": "❌ No Official Website",
                "summary": f"**{business_name}** has zero dedicated website or domain footprint on Google.",
                "flaws": [
                    "0% organic visibility on Google Search when local customers search for services",
                    "No custom domain or branded business email (lacks commercial credibility)",
                    "Losing all high-intent search traffic to local competitors with active websites",
                    "No 24/7 automated inquiry capture or appointment scheduling system"
                ],
                "suggested_service": service,
                "pricing_estimate": pricing,
                "pitch_hook": pitch
            }

        # ========================================================
        # CASE B: SOCIAL MEDIA PROFILE ONLY (Facebook, Instagram, etc.)
        # ========================================================
        social_domains = ["facebook.com", "instagram.com", "fb.me", "wa.me", "linkedin.com", "tiktok.com", "business.site"]
        if any(dom in clean_url.lower() for dom in social_domains):
            return {
                "has_website": False,
                "status": "SOCIAL_ONLY",
                "opportunity_score": "HIGH",
                "badge": "⚠️ Social Profile Only (No Dedicated Website)",
                "summary": f"**{business_name}** relies solely on a third-party social page ({clean_url[:40]}...).",
                "flaws": [
                    "Zero ownership of customer data; completely vulnerable to algorithm changes or account suspension",
                    "Cannot rank on Google Search for high-value transactional keywords",
                    "High bounce rate: users without the social app cannot view details or pricing smoothly",
                    "No integrated checkout, custom lead forms, or automated appointment calendar"
                ],
                "suggested_service": "Dedicated Business Website with Social Feed Sync",
                "pricing_estimate": "$600 – $1,500",
                "pitch_hook": (
                    f"Hi {business_name}, I saw your active social page. Most local customers search directly on Google before buying. "
                    "A dedicated website with local SEO can double your search inquiries without having to pay for Facebook ads."
                )
            }

        # ========================================================
        # CASE C: LIVE WEBSITE — FAST REAL-TIME HTTP AUDIT
        # ========================================================
        is_http_only = clean_url.startswith("http://")
        latency_ms = None
        flaws = []
        strengths = []
        page_title = ""
        has_meta_desc = False
        has_whatsapp_widget = False
        has_booking_form = False

        if is_http_only:
            flaws.append("Insecure HTTP protocol: Browsers show 'Not Secure' warning, destroying customer trust")

        try:
            start_t = time.time()
            resp = requests.get(clean_url, headers=self.headers, timeout=self.request_timeout, allow_redirects=True)
            latency_ms = int((time.time() - start_t) * 1000)

            if resp.url.startswith("http://"):
                if "Insecure HTTP protocol" not in " ".join(flaws):
                    flaws.append("Insecure HTTP: Site fails to enforce HTTPS redirection")
            else:
                strengths.append("Enforces HTTPS SSL encryption")

            if latency_ms > 2200:
                flaws.append(f"Slow mobile response time ({latency_ms}ms) — Google penalizes sites taking >2s to load")
            else:
                strengths.append(f"Fast response time ({latency_ms}ms)")

            html_text = resp.text.lower()

            # Parse title
            title_match = re.search(r"<title[^>]*>(.*?)</title>", resp.text, re.IGNORECASE | re.DOTALL)
            if title_match:
                page_title = title_match.group(1).strip()
            if not page_title or len(page_title) < 5:
                flaws.append("Missing or weak page title (Critical SEO failure)")

            # Check meta description
            if 'name="description"' in html_text or "name='description'" in html_text:
                has_meta_desc = True
                strengths.append("Contains SEO meta description")
            else:
                flaws.append("Missing SEO meta description: Google shows unformatted snippet text in search")

            # Check WhatsApp widget
            if any(wa in html_text for wa in ["wa.me", "api.whatsapp", "whatsapp.com", "joinchat"]):
                has_whatsapp_widget = True
                strengths.append("Has WhatsApp click-to-chat integration")
            else:
                flaws.append("No instant WhatsApp chat widget: Leaking mobile visitors who prefer direct messaging")

            # Check booking form
            if any(term in html_text for term in ["appointment", "booking", "calendly", "book now", "schedule", "reserve"]):
                has_booking_form = True
                strengths.append("Includes online booking / appointment feature")
            else:
                flaws.append("No online appointment or direct booking feature found")

        except requests.exceptions.Timeout:
            flaws.append("Server timeout: Website took >3.5s to respond (Extreme mobile bounce rate)")
        except requests.exceptions.SSLError:
            flaws.append("SSL Certificate Error: Site has invalid or expired SSL certificate")
        except Exception:
            flaws.append("Intermittent connectivity or website firewall blocking web crawlers")

        # Determine Score & Pitches according to Agency Target Goal
        if "ai automation" in agency_goal.lower() or "chatbot" in agency_goal.lower():
            if not has_whatsapp_widget or not has_booking_form:
                opp_score = "HIGH"
                badge = "🤖 Prime AI Chatbot Candidate (No 24/7 Booking Bot)"
                service = "24/7 AI Receptionist & WhatsApp Booking Engine"
                pricing = "$600 setup + $350/mo retainer"
                pitch = (
                    f"Hi {business_name}, we noticed your site doesn't have an instant WhatsApp booking or inquiry bot. "
                    "When customers browse after hours, they leave without booking. "
                    "We install a smart AI receptionist on WhatsApp that answers customer questions and books appointments directly into your calendar 24/7."
                )
            else:
                opp_score = "LOW"
                badge = "✅ Live Chatbot Active"
                service = "AI Workflow & CRM Integration"
                pricing = "$500/mo Retainer"
                pitch = f"Hi {business_name}, we can supercharge your current chat setup with automated CRM sync and multi-channel follow-ups."

        elif "seo" in agency_goal.lower():
            if not has_meta_desc or len(flaws) >= 2:
                opp_score = "HIGH"
                badge = "📈 Local SEO & Search Ranking Opportunity"
                service = "Google Maps & On-Page Local SEO Pack"
                pricing = "$450 – $850/mo"
                pitch = (
                    f"Hi {business_name}, we ran a local search audit on {clean_url}. "
                    "Your site is currently missing key local SEO tags and speed optimizations that keep you out of the Google Maps 3-Pack. "
                    "We can optimize your rankings to drive 30+ new local phone calls every month."
                )
            else:
                opp_score = "MEDIUM"
                badge = "⚡ Moderate SEO Opportunity"
                service = "Authority Link Building & Citations"
                pricing = "$400/mo Retainer"
                pitch = f"Hi {business_name}, we can build targeted local citations to solidify your top Google ranking in {loc_display}."

        elif "review" in agency_goal.lower() or "reputation" in agency_goal.lower():
            opp_score = "HIGH"
            badge = "⭐ Review Automation & Reputation Target"
            service = "Automated WhatsApp 5-Star Review Funnel"
            pricing = "$300 – $600/mo"
            pitch = (
                f"Hi {business_name}, 88% of local customers check reviews before choosing {cat_display}. "
                "We implement an automated WhatsApp post-visit review funnel that automatically generates 5-star Google reviews from your happy clients."
            )

        elif "paid ads" in agency_goal.lower() or "lead generation" in agency_goal.lower():
            opp_score = "HIGH"
            badge = "🎯 High-ROI Paid Ads Candidate"
            service = "High-Converting Landing Page & Google Ads"
            pricing = "$1,000 – $2,500/mo"
            pitch = (
                f"Hi {business_name}, we build high-converting landing pages and manage Google Search ad campaigns for {cat_display} in {loc_display} "
                "guaranteeing qualified appointments every single week."
            )

        else: # Website Development default
            if len(flaws) >= 3 or is_http_only:
                opp_score = "HIGH"
                badge = "🔥 High Opportunity (Multiple Conversion Bottlenecks)"
                service = "Full Website Redesign & Mobile Speed Optimization"
                pricing = "$750 – $1,800"
                pitch = (
                    f"Hi {business_name}, we ran a performance audit on {clean_url}. "
                    f"We noticed {flaws[0] if flaws else 'several conversion bottlenecks'}. "
                    "We can redesign your site for sub-second mobile loading with integrated WhatsApp lead capture in 7 days."
                )
            elif len(flaws) >= 1:
                opp_score = "MEDIUM"
                badge = "⚡ Medium Opportunity (Speed & Conversion Tweaks)"
                service = "Conversion Rate Optimization (CRO) & Speed Upgrade"
                pricing = "$400 – $900"
                pitch = (
                    f"Hi {business_name}, we checked your site {clean_url} and identified 2 quick fixes that will boost your mobile conversions by 30%."
                )
            else:
                opp_score = "LOW"
                badge = "✅ Healthy Website"
                service = "AI Automation & Chatbot Retainer"
                pricing = "$500/mo Retainer"
                pitch = f"Hi {business_name}, your website is in great health! We can add automated 24/7 WhatsApp lead capture to maximize your existing traffic."

        summary_parts = [f"Audited site: [{clean_url}]({clean_url})"]
        if page_title:
            summary_parts.append(f"Title: *\"{page_title[:50]}\"*")
        if latency_ms:
            summary_parts.append(f"Latency: `{latency_ms}ms`")

        return {
            "has_website": True,
            "status": "LIVE_WEBSITE",
            "opportunity_score": opp_score,
            "badge": badge,
            "summary": " • ".join(summary_parts),
            "flaws": flaws,
            "strengths": strengths,
            "suggested_service": service,
            "pricing_estimate": pricing,
            "pitch_hook": pitch
        }

website_auditor = WebsiteAuditor()
