import os
import re
import time
import hmac
import html
from typing import Tuple

APP_ACCESS_PASSWORD = os.getenv("APP_ACCESS_PASSWORD", "").strip()

# Regex patterns for sensitive API keys and tokens
SECRET_PATTERNS = [
    (re.compile(r"gsk_[A-Za-z0-9_]{20,}", re.IGNORECASE), "[REDACTED_GROQ_KEY]"),
    (re.compile(r"tvly-[A-Za-z0-9_\-]{20,}", re.IGNORECASE), "[REDACTED_TAVILY_KEY]"),
    (re.compile(r"sk-or-v1-[A-Za-z0-9_]{20,}", re.IGNORECASE), "[REDACTED_OPENROUTER_KEY]"),
    (re.compile(r"sk-bl-[A-Za-z0-9_]{20,}", re.IGNORECASE), "[REDACTED_BAZAARLINK_KEY]"),
    (re.compile(r"AIza[0-9A-Za-z\-_]{35}", re.IGNORECASE), "[REDACTED_GOOGLE_KEY]"),
    (re.compile(r"Bearer\s+[A-Za-z0-9_\-\.]{20,}", re.IGNORECASE), "Bearer [REDACTED_AUTH_TOKEN]"),
]

def is_auth_enabled() -> bool:
    """Returns True if an access password has been configured."""
    return bool(APP_ACCESS_PASSWORD)

def verify_access_password(input_password: str) -> bool:
    """
    Verifies the user-entered password against APP_ACCESS_PASSWORD.
    Uses hmac.compare_digest for constant-time comparison to prevent timing attacks.
    """
    if not is_auth_enabled():
        return True
    if not input_password:
        return False
    return hmac.compare_digest(input_password.strip(), APP_ACCESS_PASSWORD)

def redact_secrets(text: str) -> str:
    """
    Inspects text output from LLMs or error messages and redacts known API key patterns.
    Guarantees no raw tokens are leaked to the client browser.
    """
    if not text:
        return ""
    sanitized = str(text)
    for pattern, replacement in SECRET_PATTERNS:
        sanitized = pattern.sub(replacement, sanitized)
    return sanitized

def sanitize_html_text(text: str) -> str:
    """Escapes HTML special characters to prevent Cross-Site Scripting (XSS)."""
    if text is None:
        return ""
    return html.escape(str(text))

def check_search_cooldown(last_search_timestamp: float, cooldown_seconds: float = 4.0) -> Tuple[bool, float]:
    """
    Enforces a search cooldown per user session to mitigate Denial of Service (DoS) attacks.
    Returns (allowed, wait_seconds).
    """
    now = time.time()
    elapsed = now - last_search_timestamp
    if elapsed < cooldown_seconds:
        return False, round(cooldown_seconds - elapsed, 1)
    return True, 0.0

def clamp_lead_limit(requested_limit: int, max_cap: int = 100) -> int:
    """
    Hard-clamps lead retrieval to a maximum limit (default 100)
    to protect ephemeral memory on Render / Streamlit free tiers (512MB RAM cap).
    """
    try:
        val = int(requested_limit)
        return max(5, min(val, max_cap))
    except Exception:
        return 25
