import os
import requests
from typing import List, Dict, Optional, Any
from src.config import (
    GROQ_API_KEY,
    GROQ_BASE_URL,
    GROQ_MODELS,
    GROQ_DEFAULT_MODEL,
    OPENROUTER_API_KEY,
    OPENROUTER_DEFAULT_MODEL,
    OPENROUTER_FREE_MODELS,
    BAZAARLINK_BASE_URL,
    BAZAARLINK_API_KEY
)

class LLMHelperService:
    """
    Unified Multi-LLM Gateway providing reasoning, copywriting, and chat capabilities.
    Priority Hierarchy:
    1. ⚡ Groq (Primary Engine - Ultra-fast LPU inference: openai/gpt-oss-120b)
    2. BazaarLink AI Helper (OpenAI-compatible endpoint at https://api.bazaarlink.ai/v1)
    3. OpenRouter Free/Paid Models (Multi-model router)
    4. Built-in Expert Rule-Based Reasoning Engine (100% offline fallback)
    """

    def __init__(
        self,
        groq_key: Optional[str] = None,
        openrouter_key: Optional[str] = None,
        bazaarlink_key: Optional[str] = None,
        bazaarlink_base_url: Optional[str] = None
    ):
        self.groq_key = (groq_key or GROQ_API_KEY).strip()
        self.openrouter_key = (openrouter_key or OPENROUTER_API_KEY).strip()
        self.bazaarlink_key = (bazaarlink_key or BAZAARLINK_API_KEY).strip()
        self.bazaarlink_base_url = (bazaarlink_base_url or BAZAARLINK_BASE_URL).rstrip("/")

    def get_active_provider_name(self) -> str:
        """Returns the human-readable name of the primary active LLM provider."""
        if self.groq_key:
            return "⚡ Groq LPU (openai/gpt-oss-120b)"
        if self.bazaarlink_key:
            return "🤖 BazaarLink AI"
        if self.openrouter_key:
            return "🌐 OpenRouter"
        return "🧠 Built-in Agency Heuristics"

    def call_llm(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> Optional[str]:
        """
        Executes chat completion cascading from Groq (Tier 1) -> BazaarLink -> OpenRouter -> None.
        """
        # ========================================================
        # TIER 1: GROQ (Ultra-Fast Primary LPU Inference)
        # ========================================================
        if self.groq_key:
            headers = {
                "Authorization": f"Bearer {self.groq_key}",
                "Content-Type": "application/json"
            }
            models_to_try = [GROQ_DEFAULT_MODEL] + [m for m in GROQ_MODELS if m != GROQ_DEFAULT_MODEL]
            for model_name in models_to_try:
                try:
                    payload = {
                        "model": model_name,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }
                    resp = requests.post(
                        f"{GROQ_BASE_URL}/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=8
                    )
                    if resp.status_code == 200:
                        choices = resp.json().get("choices", [])
                        if choices:
                            content = choices[0].get("message", {}).get("content", "").strip()
                            if content:
                                return content
                except Exception:
                    continue

        # ========================================================
        # TIER 2: BAZAARLINK AI HELPER
        # ========================================================
        if self.bazaarlink_key:
            try:
                headers = {
                    "Authorization": f"Bearer {self.bazaarlink_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "auto:free",
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
                resp = requests.post(
                    f"{self.bazaarlink_base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=8
                )
                if resp.status_code == 200:
                    choices = resp.json().get("choices", [])
                    if choices:
                        content = choices[0].get("message", {}).get("content", "").strip()
                        if content:
                            return content
            except Exception:
                pass

        # ========================================================
        # TIER 3: OPENROUTER
        # ========================================================
        if self.openrouter_key:
            headers = {
                "Authorization": f"Bearer {self.openrouter_key}",
                "HTTP-Referer": "http://localhost:8501",
                "X-Title": "LeadFinder Multi-Agent System",
                "Content-Type": "application/json"
            }
            models = [OPENROUTER_DEFAULT_MODEL] + OPENROUTER_FREE_MODELS
            for model_name in models[:3]:
                try:
                    payload = {
                        "model": model_name,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }
                    resp = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=8
                    )
                    if resp.status_code == 200:
                        choices = resp.json().get("choices", [])
                        if choices:
                            content = choices[0].get("message", {}).get("content", "").strip()
                            if content:
                                return content
                except Exception:
                    continue

        return None

# Singleton instance
llm_helper = LLMHelperService()
