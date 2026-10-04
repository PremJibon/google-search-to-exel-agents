import re
import time
import requests
from typing import Dict, Any, Optional, List
from src.services.normalizer import sanitize_url, sanitize_phone, generate_whatsapp_link

class AntigravityWebsiteAuditor:
    """
    Antigravity-Style Deep Website & Digital Presence Auditing Agent.
    Autonomous multi-vector inspection:
    1. Technical Health: HTTP vs HTTPS, mobile viewport, response latency, dead/parked domain.
    2. Outdatedness Check: Copyright year analysis (detects neglected websites).
    3. Conversion & AI Readiness: WhatsApp widgets, AI chatbots, booking engines, click-to-call.
    4. Sales Weapon: Generates Antigravity Health Score (0-100), top conversion bottlenecks,
       and tailored pitch hooks across all agency service goals.
    """

    def __init__(self, request_timeout: float = 3.5):
        self.request_timeout = request_timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 AntigravityAuditor/3.0"
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
        Executes a deep Antigravity audit on a business's online presence,
        returning an objective health score (0-100), opportunity classification,
        flaw breakdown, and customized outreach pitch angles.
        """
        clean_url = sanitize_url(website) if website else ""
        clean_ph = sanitize_phone(phone) if phone else ""
        cat_display = category.title() if category else "Local Business"
        loc_display = location if location else "your local area"

        # ========================================================
        # VECTOR 1: NO WEBSITE FOUND
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

            flaws = [
                "0% organic search visibility on Google when local customers search for your services",
                "No custom domain or branded business email (damages commercial credibility)",
                "Losing high-intent search traffic to local competitors with active websites",
                "No 24/7 automated inquiry capture or appointment scheduling system"
            ]

            return {
                "has_website": False,
                "status": "NO_WEBSITE",
                "audit_score": 10,  # 10/100 Critical
                "opportunity_score": "HIGH",
                "badge": "❌ No Official Website",
                "summary": f"**{business_name}** has zero dedicated website or domain footprint on Google.",
                "flaws": flaws,
                "top_flaws": flaws[:3],
                "strengths": [],
                "suggested_service": service,
                "pricing_estimate": pricing,
                "pitch_hook": pitch
            }

        # ========================================================
        # VECTOR 2: SOCIAL MEDIA PROFILE ONLY (Facebook, Instagram, etc.)
        # ========================================================
        social_domains = ["facebook.com", "instagram.com", "fb.me", "wa.me", "linkedin.com", "tiktok.com", "linktr.ee", "business.site"]
        if any(dom in clean_url.lower() for dom in social_domains):
            flaws = [
                "Zero ownership of customer data; completely vulnerable to social platform algorithm shifts or account lockouts",
                "Cannot rank in Google Maps 3-Pack or Google Search for high-value buyer search queries",
                "High mobile bounce rate: visitors without the social app installed face login walls",
                "Lacks professional credibility, custom email domain, and automated booking calendar"
            ]
            return {
                "has_website": False,
                "status": "SOCIAL_ONLY",
                "audit_score": 28,  # 28/100 Poor
                "opportunity_score": "HIGH",
                "badge": "⚠️ Social Profile Only (No Dedicated Website)",
                "summary": f"**{business_name}** relies solely on a third-party social link ({clean_url[:40]}...).",
                "flaws": flaws,
                "top_flaws": flaws[:3],
                "strengths": ["Active social presence"],
                "suggested_service": "Dedicated Business Website with Social Feed Sync",
                "pricing_estimate": "$600 – $1,500",
                "pitch_hook": (
                    f"Hi {business_name}, I saw your active social page. Most local customers search directly on Google before buying. "
                    "A dedicated website with local SEO can double your search inquiries without having to pay for Facebook ads."
                )
            }

        # ========================================================
        # VECTOR 3: LIVE WEBSITE — REAL-TIME ANTIGRAVITY DEEP AUDIT
        # ========================================================
        is_http_only = clean_url.startswith("http://")
        latency_ms = None
        flaws: List[str] = []
        strengths: List[str] = []
        page_title = ""
        has_meta_desc = False
        has_viewport = False
        has_whatsapp_widget = False
        has_booking_form = False
        has_click_to_call = False
        outdated_year = None
        is_parked_domain = False
        tech_stack = []

        if is_http_only:
            flaws.append("Insecure HTTP protocol: Browsers show 'Not Secure' warning, destroying customer trust")

        try:
            start_t = time.time()
            resp = requests.get(clean_url, headers=self.headers, timeout=self.request_timeout, allow_redirects=True)
            latency_ms = int((time.time() - start_t) * 1000)

            # Check HTTP Status Code for Dead / Broken links
            if resp.status_code in (404, 410):
                flaws.append(f"Dead link: Website returns HTTP {resp.status_code} Not Found error")
            elif resp.status_code >= 500:
                flaws.append(f"Server crash: Website returns HTTP {resp.status_code} Internal Server Error")

            if resp.url.startswith("http://"):
                if "Insecure HTTP protocol" not in " ".join(flaws):
                    flaws.append("Insecure HTTP: Site fails to enforce HTTPS redirection")
            else:
                strengths.append("Enforces HTTPS SSL encryption")

            if latency_ms > 2500:
                flaws.append(f"Slow mobile response time ({latency_ms}ms) — Google penalizes sites taking >2s to load")
            else:
                strengths.append(f"Fast response time ({latency_ms}ms)")

            html_text = resp.text.lower()

            # Check for Parked / For-Sale Domain
            parked_patterns = [
                "domain is for sale", "buy this domain", "parked free", "hugedomains",
                "godaddy.com/forsale", "dan.com/buy-domain", "namecheap parking", "under construction"
            ]
            if any(p in html_text for p in parked_patterns) and len(html_text) < 15000:
                is_parked_domain = True
                flaws.append("Parked / Placeholder domain: The domain does not host an active business website")

            # Parse Page Title
            title_match = re.search(r"<title[^>]*>(.*?)</title>", resp.text, re.IGNORECASE | re.DOTALL)
            if title_match:
                page_title = title_match.group(1).strip()
            if not page_title or len(page_title) < 5:
                flaws.append("Missing or weak page title (Critical SEO failure)")
            else:
                strengths.append(f"Title configured: '{page_title[:35]}'")

            # Meta Viewport (Mobile Responsiveness)
            if 'name="viewport"' in html_text or "name='viewport'" in html_text:
                has_viewport = True
                strengths.append("Mobile viewport meta tag configured")
            else:
                flaws.append("Missing mobile viewport: Website does not scale properly on smartphones")

            # Meta Description
            if 'name="description"' in html_text or "name='description'" in html_text:
                has_meta_desc = True
                strengths.append("Contains SEO meta description")
            else:
                flaws.append("Missing SEO meta description: Google shows unformatted snippet text in search")

            # Outdated Copyright Year Check
            copy_match = re.search(r'(?:©|&copy;|copyright|all rights reserved)[^\d]{0,20}(20[0-2]\d)', html_text)
            if copy_match:
                found_year = int(copy_match.group(1))
                if found_year <= 2022:
                    outdated_year = found_year
                    flaws.append(f"Outdated copyright notice ({found_year}): Website appears neglected/unmaintained")
                else:
                    strengths.append(f"Recently updated copyright ({found_year})")

            # WhatsApp Click-to-Chat Widget
            if any(wa in html_text for wa in ["wa.me", "api.whatsapp", "whatsapp.com", "joinchat", "chat-widget"]):
                has_whatsapp_widget = True
                strengths.append("Has WhatsApp click-to-chat integration")
            else:
                flaws.append("No instant WhatsApp chat widget: Leaking mobile visitors who prefer direct messaging")

            # Online Booking / Appointment System
            booking_terms = ["appointment", "booking", "calendly", "book now", "schedule", "reserve", "fresha", "booksy", "acuity"]
            if any(term in html_text for term in booking_terms):
                has_booking_form = True
                strengths.append("Includes online booking / appointment feature")
            else:
                flaws.append("No online appointment or direct booking feature found")

            # Click-to-call Phone Link
            if 'href="tel:' in html_text or "href='tel:" in html_text:
                has_click_to_call = True
                strengths.append("Includes 1-click mobile phone calling link")
            else:
                flaws.append("No click-to-call phone button for frictionless mobile dialing")

            # CMS & Framework Detection
            if "wp-content" in html_text:
                tech_stack.append("WordPress")
            elif "wix.com" in html_text:
                tech_stack.append("Wix")
            elif "squarespace" in html_text:
                tech_stack.append("Squarespace")
            elif "shopify" in html_text:
                tech_stack.append("Shopify")

        except requests.exceptions.Timeout:
            flaws.append("Server timeout: Website took >3.5s to respond (Extreme mobile bounce rate)")
        except requests.exceptions.SSLError:
            flaws.append("SSL Certificate Error: Site has invalid or expired SSL certificate")
        except requests.exceptions.ConnectionError:
            flaws.append("Connection Refused / Dead Site: Website server is unreachable")
        except Exception as e:
            flaws.append(f"Site unreachable: {str(e)[:40]}")

        # Compute Antigravity Health Score (0 - 100)
        score = 100
        if is_parked_domain:
            score = 15
        elif any("Dead link" in f or "Server crash" in f or "Connection Refused" in f for f in flaws):
            score = 12
        else:
            if is_http_only or any("Insecure HTTP" in f for f in flaws):
                score -= 25
            if any("SSL Certificate Error" in f for f in flaws):
                score -= 30
            if not has_viewport:
                score -= 25
            if not has_whatsapp_widget:
                score -= 15
            if not has_booking_form:
                score -= 15
            if not has_click_to_call:
                score -= 10
            if not has_meta_desc:
                score -= 10
            if outdated_year:
                score -= 15
            if latency_ms and latency_ms > 2500:
                score -= 10

        score = max(5, min(98, score))

        # Classify Opportunity Score based on Antigravity Score
        if score < 45 or is_parked_domain:
            opp_score = "HIGH"
        elif score < 75:
            opp_score = "MEDIUM"
        else:
            opp_score = "LOW"

        # Determine Service & Badges according to Agency Target Goal
        if is_parked_domain:
            badge = "🚨 Parked Domain (No Active Site)"
            service = "New Website Development & Brand Launch"
            pricing = "$700 – $1,500"
            pitch = (
                f"Hi {business_name}, I checked {clean_url} and noticed it's currently showing a domain parking page. "
                "Local customers searching for your services are unable to view your business or get in touch. "
                "We can launch a high-converting mobile website with WhatsApp booking in just 5 days."
            )
        elif any("Dead link" in f or "Connection Refused" in f for f in flaws):
            badge = "🚨 Broken Website (404/Down)"
            service = "Emergency Website Rebuild & Hosting"
            pricing = "$500 – $1,200"
            pitch = (
                f"Hi {business_name}, I tried visiting {clean_url} and your website is currently down/broken. "
                "You are losing every customer who tries to click through from Google. "
                "We can get a clean, reliable website back online for you immediately."
            )
        elif "ai automation" in agency_goal.lower() or "chatbot" in agency_goal.lower():
            if not has_whatsapp_widget or not has_booking_form:
                badge = "🤖 Prime AI Chatbot Candidate (No 24/7 Booking Bot)"
                service = "24/7 AI Receptionist & WhatsApp Booking Engine"
                pricing = "$600 setup + $350/mo retainer"
                pitch = (
                    f"Hi {business_name}, we noticed your site doesn't have an instant WhatsApp booking or inquiry bot. "
                    "When customers browse after hours, they leave without booking. "
                    "We install a smart AI receptionist on WhatsApp that answers customer questions and books appointments directly into your calendar 24/7."
                )
            else:
                badge = "✅ Live Chatbot Active"
                service = "AI Workflow & CRM Integration"
                pricing = "$500/mo Retainer"
                pitch = f"Hi {business_name}, we can supercharge your current chat setup with automated CRM sync and multi-channel follow-ups."

        elif "seo" in agency_goal.lower():
            if not has_meta_desc or len(flaws) >= 2:
                badge = "📈 Local SEO & Search Ranking Opportunity"
                service = "Google Maps & On-Page Local SEO Pack"
                pricing = "$450 – $850/mo"
                pitch = (
                    f"Hi {business_name}, we ran an Antigravity local SEO audit on {clean_url}. "
                    "Your site is currently missing key local SEO tags and speed optimizations that keep you out of the Google Maps 3-Pack. "
                    "We can optimize your rankings to drive 30+ new local phone calls every month."
                )
            else:
                badge = "⚡ Moderate SEO Opportunity"
                service = "Authority Link Building & Citations"
                pricing = "$400/mo Retainer"
                pitch = f"Hi {business_name}, we can build targeted local citations to solidify your top Google ranking in {loc_display}."

        else: # Website Development default
            if score < 50:
                badge = "🔥 High Opportunity (Severe Technical/Conversion Flaws)"
                service = "Full Website Redesign & Mobile Speed Optimization"
                pricing = "$750 – $1,800"
                pitch = (
                    f"Hi {business_name}, we ran an Antigravity health check on {clean_url} (Score: {score}/100). "
                    f"We identified critical conversion issues: {flaws[0] if flaws else 'unresponsive mobile layout'}. "
                    "We can redesign your site for sub-second mobile loading with integrated WhatsApp lead capture in 7 days."
                )
            elif score < 75:
                badge = "⚡ Medium Opportunity (Conversion & Speed Tweaks)"
                service = "Conversion Rate Optimization (CRO) & Mobile Upgrade"
                pricing = "$400 – $900"
                pitch = (
                    f"Hi {business_name}, we checked your site {clean_url} (Health Score: {score}/100) and identified 2 quick fixes that will boost your mobile conversions by 30%."
                )
            else:
                badge = "✅ Healthy Website"
                service = "AI Automation & Chatbot Retainer"
                pricing = "$500/mo Retainer"
                pitch = f"Hi {business_name}, your website is in great health! We can add automated 24/7 WhatsApp lead capture to maximize your existing traffic."

        summary_parts = [f"Audited site: [{clean_url}]({clean_url})", f"Health Score: **{score}/100**"]
        if page_title:
            summary_parts.append(f"Title: *\"{page_title[:40]}\"*")
        if latency_ms:
            summary_parts.append(f"Latency: `{latency_ms}ms`")

        return {
            "has_website": True,
            "status": "LIVE_WEBSITE",
            "audit_score": score,
            "opportunity_score": opp_score,
            "badge": badge,
            "summary": " • ".join(summary_parts),
            "flaws": flaws,
            "top_flaws": flaws[:3],
            "strengths": strengths,
            "suggested_service": service,
            "pricing_estimate": pricing,
            "pitch_hook": pitch,
            "tech_stack": tech_stack
        }

website_auditor = AntigravityWebsiteAuditor()
