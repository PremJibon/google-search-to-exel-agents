# System Architecture & Technical Specifications (v2.1)

## 1. High-Level Architecture Overview

```mermaid
flowchart TD
    User["Agency Owner / User"] --> Gate["Zero-Trust Security Gate\n(HMAC Constant-Time Passkey)"]
    Gate --> UI["Frontend UI (Streamlit SaaS)"]

    subgraph AgentTeam ["Named AI Agency Team"]
        Nova["🔭 Nova (Scout)\n[Discovery & Geocoding]"]
        Max["🔍 Max (Auditor)\n[Tech & Opportunity Audit]"]
        Apex["📢 Apex (Marketer)\n[Cold Pitch & Closing Strategy]"]
        Atlas["🧭 Atlas (Strategist)\n[Agency Scaling & Operations]"]
    end

    subgraph ProviderLayer ["Data & Intelligence Layer"]
        OSM["OpenStreetMap Overpass API\n[100% Free - Default]"]
        Tavily["Tavily Deep Search API\n[Web Footprint & Phone Lookup]"]
        Serper["Google Maps via Serper\n[2,500 Free Tier]"]
    end

    subgraph AIEngines ["Multi-LLM Intelligence Gateway (llm_helper)"]
        Groq["⚡ Groq LPU (openai/gpt-oss-120b)\n[Tier 1 - Primary 500 tokens/sec]"]
        BazaarLink["🤖 BazaarLink AI Helper\n[Tier 2 - OpenAI Compatible]"]
        OpenRouter["🌐 OpenRouter Gateway\n[Tier 3 - Multi-Model Backup]"]
        Offline["🧠 Built-in Agency Heuristics\n[Tier 4 - 100% Offline Engine]"]
    end

    subgraph SecurityShield ["6-Layer Security Shield"]
        FilterRedact["Output Secret Redaction Filter"]
        FormulaDef["CSV/Excel Formula Injection Defense"]
        RateLimit["4-Second Search Cooldown & 100-Lead Cap"]
    end

    subgraph OutputLayer ["Presentation & Export"]
        Table["Interactive Live Leads Table"]
        Map["Geocoded Geographic Map View"]
        Chat["Agency Multi-Agent Chatroom"]
        Excel["In-Memory XLSX Generator (xlsxwriter)"]
        CSV["In-Memory UTF-8 CSV Streamer"]
    end

    UI --> Nova
    Nova --> ProviderLayer
    ProviderLayer --> Max
    Max -->|"High-Need Businesses Flagged"| Nova
    Nova -->|"Deep Search Phone/Web Enrichment"| Max
    Max --> Apex
    AgentTeam <--> AIEngines
    AgentTeam --> SecurityShield
    SecurityShield --> OutputLayer
    OutputLayer --> UI
```

---

## 2. Technology Stack & Rationale

| Component | Selected Technology | Alternative Considered | Rationale | Cost |
| :--- | :--- | :--- | :--- | :--- |
| **Language** | Python 3.11 - 3.14 | TypeScript / Node.js | Fast data processing, rich ecosystem | **$0** (FOSS) |
| **User Interface** | Streamlit | Next.js + React | Zero boilerplate, native live progress, instant memory downloads | **$0** (FOSS) |
| **Primary AI Engine** | **Groq LPU** (`openai/gpt-oss-120b`) | OpenAI GPT-4o / Anthropic | 500+ tokens/sec, sub-second latency, generous free tier | **$0** (Free Tier) |
| **Helper AI** | BazaarLink AI (`api.bazaarlink.ai/v1`) | Local Ollama | Fast OpenAI-compatible assistant | **$0** (Free Tier) |
| **Deep Search** | Tavily Search API | Direct HTML Scraping | High-accuracy business footprint, contact & phone lookup | **$0** (1k Free/mo) |
| **Free Map Data** | OpenStreetMap (Overpass + Nominatim) | Direct Google Scraping | Legal, stable, unmetered, keyless | **$0** (FOSS) |
| **Spreadsheet Engine**| `xlsxwriter` | SheetJS | High performance Excel generation with styling, auto-width, frozen headers | **$0** (FOSS) |
| **Security Shield** | `hmac`, regex redaction, formula escaping | Cloudflare WAF | Built-in zero-trust passkey, anti-injection, and rate-limiting | **$0** (Native) |
| **Hosting Target** | Streamlit Community Cloud / Render Free | AWS / GCP Paid | 100% free hosting forever, custom domains, free SSL | **$0** |

---

## 3. Collaborative Dual-Agent Handshake Loop

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant UI as Streamlit SaaS UI
    participant Pipe as LeadPipeline
    participant Nova as 🔭 Nova (Scout)
    participant Max as 🔍 Max (Auditor)
    participant Tavily as 🌐 Tavily Deep Search
    participant Apex as 📢 Apex (Digital Marketer)

    User->>UI: Submit Search ("Gym", "Kamalapur, Dhaka", Goal: "AI Automation")
    UI->>Pipe: run(params)
    Pipe->>Nova: Geocode & Scan POIs
    Nova-->>Pipe: Return 10 Discovered Gyms (Raw)
    Pipe->>Max: Initial Audit (Inspect websites, phones, categories)
    Max-->>Pipe: Flag 4 High-Priority Prospects (Missing Website or Phone)
    Pipe->>Nova: Trigger Deep Search on Flagged Prospects
    Nova->>Tavily: Search: "{business_name} {city} phone contact website"
    Tavily-->>Nova: Extract Official Website, Social Link, and Phone (+880...)
    Nova-->>Pipe: Enriched Lead Records
    Pipe->>Max: Re-audit Enriched Leads (Assign Service: 24/7 AI Receptionist)
    Pipe->>Apex: Synthesize Cold WhatsApp Pitch & Closing Angles
    Apex-->>Pipe: Completed Qualified Lead Dataset
    Pipe->>UI: Render Table, Map, and Chat Context
```

---

## 4. Multi-Layer Security Architecture

### 4.1. Zero-Trust Access Gatekeeper
- Validates user input against `APP_ACCESS_PASSWORD` using `hmac.compare_digest()` to prevent timing attacks.
- If password is unset in `.env`, application runs in open development mode.

### 4.2. Automated Output Redaction Filter
- Intercepts all LLM and agent outputs before rendering to the client browser.
- Automatically redacts regex patterns for `gsk_`, `tvly-`, `sk-or-`, `sk-bl-`, and Bearer tokens.

### 4.3. Spreadsheet Formula Injection Defense
- Every text cell exported to `.xlsx` or `.csv` is inspected by `sanitize_formula_injection()`.
- Prepends a single quote `'` to any cell starting with `=`, `+`, `-`, `@`, `|`, `\t`, or `\r`.

### 4.4. Memory & DoS Shield (512MB RAM Cap)
- Hard clamp enforcing maximum limit of 100 leads per query.
- 4-second minimum search cooldown per user session.
- Explicit `gc.collect()` and buffer dereferencing upon file streaming.
