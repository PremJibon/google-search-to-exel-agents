import re
from urllib.parse import urlparse, urlunparse

def sanitize_phone(raw_phone: str) -> str:
    """
    Cleans raw phone numbers.
    Preserves leading '+' for international numbers, strips non-numeric noise.
    Returns empty string if invalid or under 7 digits.
    """
    if not raw_phone:
        return ""
        
    s = str(raw_phone).strip()
    
    # Handle multiple numbers separated by slash or comma, take primary
    if "/" in s:
        s = s.split("/")[0].strip()
    if ";" in s:
        s = s.split(";")[0].strip()
    if "," in s:
        s = s.split(",")[0].strip()

    # If starts with 00, convert to +
    if s.startswith("00"):
        s = "+" + s[2:]

    has_plus = s.startswith("+")
    digits = re.sub(r"\D", "", s)

    # Valid phone numbers are between 7 and 15 digits
    if len(digits) < 7 or len(digits) > 15:
        return ""

    return f"+{digits}" if has_plus else digits

def sanitize_url(raw_url: str) -> str:
    """
    Sanitizes website URLs, normalizes protocol, strips tracking tags.
    """
    if not raw_url:
        return ""
        
    url = str(raw_url).strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        parsed = urlparse(url)
        # Drop tracking query params
        clean_url = urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path,
            '',  # params
            '',  # query stripped to prevent tracking tags
            ''   # fragment
        ))
        return clean_url.rstrip("/")
    except Exception:
        return ""

def sanitize_formula_injection(value: any) -> str:
    """
    Guards against CSV / Excel Formula Injection (CSV Injection).
    Prepends a single quote if the string begins with risky spreadsheet triggers.
    """
    if value is None:
        return ""
    text = str(value).strip()
    if text.startswith(("=", "+", "-", "@", "\t", "\r", "|")):
        return "'" + text
    return text

def format_address_from_tags(tags: dict) -> str:
    """
    Extracts structured address components from OSM tags:
    addr:housenumber, addr:street, addr:suburb, addr:city, addr:postcode
    """
    parts = []
    
    # House number + Street
    street_parts = []
    if tags.get("addr:housenumber"):
        street_parts.append(tags["addr:housenumber"])
    if tags.get("addr:street"):
        street_parts.append(tags["addr:street"])
    if street_parts:
        parts.append(" ".join(street_parts))

    # Suburb / Area
    if tags.get("addr:suburb"):
        parts.append(tags["addr:suburb"])
    elif tags.get("addr:neighbourhood"):
        parts.append(tags["addr:neighbourhood"])

    # City / District
    if tags.get("addr:city"):
        parts.append(tags["addr:city"])
    elif tags.get("addr:district"):
        parts.append(tags["addr:district"])

    # Postcode
    if tags.get("addr:postcode"):
        parts.append(tags["addr:postcode"])

    return ", ".join(parts) if parts else tags.get("address", "")
