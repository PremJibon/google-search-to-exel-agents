import requests
from typing import Optional
from src.config import OPENROUTER_API_KEY, OPENROUTER_DEFAULT_MODEL, OPENROUTER_FREE_MODELS

class OpenRouterAIService:
    """
    AI Reasoning & Copywriting engine powered by OpenRouter free-tier LLMs.
    Used by Agent 2 (Auditor) to craft custom, highly persuasive sales pitches.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = OPENROUTER_DEFAULT_MODEL):
        self.api_key = (api_key or OPENROUTER_API_KEY).strip()
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    @property
    def is_available(self) -> bool:
        return bool(self.api_key)

    def generate_personalized_pitch(
        self,
        business_name: str,
        category: str,
        city: str,
        opportunity_type: str,
        suggested_service: str,
        agency_goal: str
    ) -> Optional[str]:
        """
        Uses OpenRouter free LLM to generate a personalized, high-converting cold outreach pitch.
        """
        if not self.is_available:
            return None

        prompt = (
            f"You are a top B2B sales outreach copywriter for a digital agency. "
            f"Write a short, highly persuasive, 2-to-3 sentence cold outreach message (suitable for WhatsApp or email) to a business owner.\n\n"
            f"Business: {business_name}\n"
            f"Category: {category}\n"
            f"City: {city}\n"
            f"Agency Service to Sell: {suggested_service} (Goal: {agency_goal})\n"
            f"Detected Flaw/Opportunity: {opportunity_type}\n\n"
            f"Rules:\n"
            f"- Sound authentic, warm, and professional. Not spammy or robotic.\n"
            f"- Directly address how fixing this flaw will bring them more local paying customers.\n"
            f"- Output ONLY the message text, no subject lines or commentary."
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://localhost:8501",
            "X-Title": "LeadFinder Agency Agent",
            "Content-Type": "application/json"
        }

        # Try default model, fallback to secondary free model if needed
        models_to_try = [self.model] + [m for m in OPENROUTER_FREE_MODELS if m != self.model]

        for m in models_to_try[:2]:
            try:
                payload = {
                    "model": m,
                    "messages": [
                        {"role": "system", "content": "You write concise, punchy B2B sales outreach."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 160
                }

                resp = requests.post(self.base_url, headers=headers, json=payload, timeout=8)
                if resp.status_code == 200:
                    data = resp.json()
                    choices = data.get("choices", [])
                    if choices:
                        content = choices[0].get("message", {}).get("content", "").strip()
                        if content:
                            return content.strip('"')
            except Exception:
                continue

        return None
