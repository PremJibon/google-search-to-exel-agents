# AI Agent Specification (`agent.md`)

## 1. Agent Mission & Persona
The **LeadFinder Agent** is an autonomous, reliable, cost-conscious data retrieval agent designed to parse geographic and business search intents, query verified public data sources, execute rigorous data cleansing/deduplication, and deliver sales-ready lead sheets.

### Core Guiding Principles:
1. **Zero Hallucination**: Never invent names, phone numbers, addresses, ratings, or websites. If a field is missing from the data source, mark it empty.
2. **Zero Unapproved Cost**: Never invoke paid APIs, proxy networks, or services requiring credit cards without explicit user confirmation.
3. **Deterministic First**: Retain deterministic Python code for API fetching, data cleansing, deduplication, and export. Use LLM capabilities solely for interpreting ambiguous user text or classifying business taxonomy.
4. **Resilient & Transparent**: Report real-time execution steps, rate-limit warnings, and recovery actions directly to the user.

---

## 2. Agent Tool Inventory & Schemas

The agent operates strictly through defined functional tools with typed inputs and outputs:

### Tool 1: `geocode_location`
- **Purpose**: Converts natural-language location terms into geographic coordinates and bounding boxes.
- **Input Schema**:
  ```json
  {
    "country": "string (e.g., 'India')",
    "city": "string (e.g., 'Bangalore')",
    "area": "string (e.g., 'Koramangala')"
  }
  ```
- **Output Schema**:
  ```json
  {
    "status": "SUCCESS | NOT_FOUND | ERROR",
    "display_name": "Koramangala, Bangalore, Bengaluru Urban, Karnataka, 560034, India",
    "lat": 12.9352,
    "lon": 77.6245,
    "bounding_box": {
      "south": 12.915,
      "west": 77.605,
      "north": 12.955,
      "east": 77.645
    },
    "error_message": null
  }
  ```

---

### Tool 2: `search_businesses`
- **Purpose**: Executes query against the active provider (e.g., OpenStreetMap Overpass) within geographic boundaries.
- **Input Schema**:
  ```json
  {
    "bounding_box": {
      "south": "float",
      "west": "float",
      "north": "float",
      "east": "float"
    },
    "category": "string (e.g., 'restaurant', 'dentist', 'gym')",
    "keyword": "string | null",
    "max_results": "integer (1 to 200)"
  }
  ```
- **Output Schema**:
  ```json
  {
    "status": "SUCCESS | EMPTY | PROVIDER_ERROR",
    "total_found": 35,
    "leads": [
      {
        "id": "node/12345678",
        "name": "Brahmin's Coffee Bar",
        "phone": "+91 80 2660 1234",
        "address": "Shankarapura, Bangalore",
        "website": "http://brahminscoffeebar.com",
        "maps_link": "https://www.openstreetmap.org/node/12345678",
        "category": "restaurant",
        "lat": 12.9431,
        "lon": 77.5712,
        "raw_tags": { ... }
      }
    ]
  }
  ```

---

### Tool 3: `normalize_lead`
- **Purpose**: Sanitizes phone numbers, normalizes URLs, trims messy whitespace, and standardizes casing.
- **Input Schema**: Raw lead dictionary.
- **Rules**:
  - Phone: Clean punctuation `+91 (080) 1234 5678` ➔ `+918026601234`
  - URL: Prepend `https://` if protocol missing, strip `utm_*` and session parameters.
  - Text: Normalize whitespace, unescape HTML entities.

---

### Tool 4: `deduplicate_leads`
- **Purpose**: Eliminates duplicate entries caused by overlapping nodes/ways or multiple tags.
- **Methodology**:
  1. Exact match on normalized phone number or normalized website domain.
  2. Fuzzy match on Business Name (Levenshtein / Token Set Ratio > 88%) combined with geographical distance (< 150m).

---

### Tool 5: `export_dataset`
- **Purpose**: Generates high-quality Excel (`.xlsx`) and CSV byte streams.
- **Format**:
  - Sheet Name: `Leads`
  - Headers: `Business Name`, `Phone`, `Address`, `Website`, `Maps Link`, `Category`, `Source`
  - Styling: Freeze top row, bold header with dark theme, auto-fit column widths (max 50 chars).

---

## 3. Natural Language Interpretation (Optional AI Step)

When a user provides free-form input (e.g., *"Find 30 dental clinics around Koramangala, Bangalore with phone numbers"*), the agent maps the prompt into structured search parameters:

```json
{
  "country": "India",
  "city": "Bangalore",
  "area": "Koramangala",
  "category": "dentist",
  "keyword": null,
  "max_results": 30,
  "require_phone": true,
  "require_website": false
}
```

If no LLM API key is present, the app defaults to standard dashboard form inputs, ensuring zero external LLM dependency is ever required.
