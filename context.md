# Context Engine & Runtime State Specification (`context.md`)

## 1. Overview
The Context Engine maintains application runtime state, coordinates progress updates between the background pipeline and frontend UI, manages memory and token budgets, and triggers self-review and recovery procedures.

---

## 2. Progress Triggers & Pipeline State Machine

The pipeline emits standard event triggers at each execution phase so the UI can update live without page freeze.

| Phase ID | Trigger Name | Progress % | Description & Payload |
| :--- | :--- | :--- | :--- |
| `PHASE_INIT` | `search_started` | 5% | Search query received, inputs validated. |
| `PHASE_GEO` | `geocoding_active` | 20% | Resolving boundary & coordinates via Nominatim. Payload: `{area, city, country}` |
| `PHASE_GEO_DONE`| `geocoding_success` | 35% | Bounding box identified. Payload: `{display_name, lat, lon}` |
| `PHASE_FETCH` | `querying_provider` | 50% | Fetching POIs from Overpass/Google. Payload: `{provider, category}` |
| `PHASE_EXTRACT`| `extracting_records`| 70% | Parsing tags, phones, addresses. Payload: `{raw_count}` |
| `PHASE_CLEAN` | `normalizing_records`| 80% | Cleansing phone numbers, URLs, and text fields. |
| `PHASE_DEDUP` | `deduplicating` | 90% | Removing duplicate POIs by proximity and name similarity. |
| `PHASE_FILTER`| `filtering_results` | 95% | Enforcing filters (`require_phone`, `require_website`, `max_results`). |
| `PHASE_READY` | `pipeline_completed`| 100% | Final dataset ready for interactive table & instant download. |

### Progress Trigger Callback Interface
```python
from typing import Callable, Optional

ProgressCallback = Callable[[int, str, Optional[dict]], None]
# progress_callback(progress_percent: int, status_message: str, metadata: dict)
```

---

## 3. Token & Resource Management (Budgeting)

### 3.1. Zero-Token Baseline (Deterministic Default)
- **Default Operation**: 0 LLM tokens consumed.
- Search queries from the standard dashboard form bypass LLM completely, routing directly to deterministic geocoding and Overpass QL builders.

### 3.2. Optional AI Parsing (Natural Language Mode)
- **Token Cap per Request**: Max 500 input tokens, 200 output tokens.
- **Model Compatibility**: Free-tier Gemini (`gemini-1.5-flash`), Groq (`llama-3-8b`), or local Ollama.
- **Prompt Guardrail**: One-shot system prompt returning strictly JSON schema. No multi-turn chat bloating context.

### 3.3. Memory Management (512 MB Render Free Tier Limit)
- Render Free instances provide **512 MB RAM**.
- Lead lists are stored as lightweight Python dictionaries or slim pandas DataFrames.
- Maximum search limit is capped at **200 leads per query** to prevent Out-Of-Memory (OOM) crashes.
- Excel and CSV generation uses direct memory buffers (`io.BytesIO()`) and garbage collection is triggered upon delivery.

---

## 4. UI Context & Session State Structure

In Streamlit or Next.js, the session context maintains:

```python
{
    "search_params": {
        "country": "India",
        "city": "Bangalore",
        "area": "Koramangala",
        "category": "restaurant",
        "keyword": "",
        "limit": 50,
        "require_phone": True,
        "require_website": False
    },
    "runtime_state": {
        "is_searching": False,
        "current_step": "IDLE",
        "progress_percent": 0,
        "status_message": "Ready to search",
        "error": None
    },
    "data_state": {
        "raw_leads": [],
        "processed_leads": [],
        "filtered_count": 0,
        "excel_buffer": None,
        "csv_buffer": None
    },
    "provider_state": {
        "active_provider": "OpenStreetMap",
        "has_google_key": False,
        "api_call_count": 0
    }
}
```

---

## 5. Agent Skill Hooks
The context engine triggers specialized skill workflows upon state transitions:
1. **Validation & Review Trigger**: Run `skills/review_skill.md` before returning results to UI to verify zero hallucination and clean schemas.
2. **Failure Recovery Trigger**: Run `skills/recover_skill.md` if an Overpass endpoint times out or Nominatim returns zero coordinates.
