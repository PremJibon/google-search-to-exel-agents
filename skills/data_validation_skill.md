# Data Validation Skill (`skills/data_validation_skill.md`)

## 1. Purpose
The **Data Validation Skill** defines and enforces schemas, data types, string sanitization, and output invariants for all data flowing through the LeadFinder pipeline.

---

## 2. Invariant Rules & Data Dictionary

### Standard Lead Data Schema
| Column Name | Data Type | Permitted Null? | Validation Rule | Example |
| :--- | :--- | :--- | :--- | :--- |
| `Business Name` | `string` | **No** | Trimmed, 1-200 characters, no HTML tags | "Toit Brewpub" |
| `Phone` | `string` | **Yes** | E.164 or standardized local phone format, 7-15 digits | "+918025201105" |
| `Address` | `string` | **Yes** | Street, neighborhood, city, postal code | "100 Feet Rd, Indiranagar, Bangalore" |
| `Website` | `string` | **Yes** | Valid URI syntax, lowercase host | "https://toit.in" |
| `Maps Link` | `string` | **No** | Valid OpenStreetMap or Google Maps URI | "https://www.openstreetmap.org/node/12345" |
| `Category` | `string` | **No** | Canonical category name | "Restaurant" |
| `Source` | `string` | **No** | Origin provider | "OpenStreetMap" |
| `Status` | `string` | **No** | Enum: `FOUND`, `MISSING_PHONE`, `MISSING_WEBSITE` | "FOUND" |

---

## 3. Sanitization Pipelines

### 3.1. Phone Sanitizer
```python
import re

def sanitize_phone(raw_phone: str) -> str:
    if not raw_phone:
        return ""
    # Strip spaces, dashes, dots, brackets
    cleaned = re.sub(r"[^\d+]", "", raw_phone.strip())
    # Ensure minimum valid phone length
    digits = re.sub(r"\D", "", cleaned)
    if len(digits) < 7:
        return ""
    return cleaned
```

### 3.2. URL Sanitizer
```python
from urllib.parse import urlparse, urlunparse

def sanitize_url(raw_url: str) -> str:
    if not raw_url:
        return ""
    url = raw_url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    parsed = urlparse(url)
    # Strip query parameters containing tracking tags
    clean_url = urlunparse((parsed.scheme, parsed.netloc.lower(), parsed.path, '', '', ''))
    return clean_url.rstrip("/")
```

### 3.3. CSV Formula Injection Defense
Prevents execution of malicious payloads when exported files are opened in Microsoft Excel or Google Sheets:
```python
def sanitize_cell_value(val: any) -> str:
    if val is None:
        return ""
    text = str(val).strip()
    if text.startswith(("=", "+", "-", "@", "\t", "\r")):
        return "'" + text
    return text
```
