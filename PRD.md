# Product Requirements Document (PRD)
## Local Business Lead Generation Agent ("LeadFinder Free")

### 1. Executive Summary & Core Objective
The **Local Business Lead Finder & Agency Qualifier** is a lightweight, free-first web application powered by a **Two-Agent System**:
1. **Discovery Agent (Scouter)**: Discovers local businesses in the target area (OpenStreetMap, Tavily Search API, or Google Maps) and extracts Name, Phone, Address, Website, and Maps Link.
2. **Qualification & Audit Agent (Auditor)**: Audits the discovered leads against specific agency service criteria—such as **Selling Websites** (detecting missing/broken websites) or **Selling AI Automation & Chatbots** (evaluating inquiry volume, appointment booking needs, and digital readiness)—assigning a Lead Opportunity Score and a tailored outreach pitch angle.

**Primary Flow:**
`Location + Category + Agency Target Mode (Websites / AI Automation / General)` ➔ `Agent 1: Discovery` ➔ `Agent 2: Qualification Audit` ➔ `Live UI Table + Map` ➔ `Excel (XLSX) / CSV Export with Outreach Angles`

---

### 2. Agency Lead Target Modes
- **Mode 1: Website Design & Development Clients**
  - Targets businesses that have **NO website**, or only link to a basic Facebook/Instagram page, or have unencrypted HTTP links.
  - Generates pitch angle: *"High-priority prospect: No official website. Pitch modern responsive website & local SEO."*
- **Mode 2: AI Automation & Chatbot Clients**
  - Targets high-inquiry businesses (e.g. dental clinics, gyms, salons, car repair, restaurants) that handle repetitive phone calls and appointments.
  - Generates pitch angle: *"Prime candidate for 24/7 AI receptionist, appointment booking bot, and WhatsApp auto-responder."*
- **Mode 3: Local SEO & Google Business Profile Optimization**
  - Targets businesses with missing contact details, unverified listings, or incomplete web presence.
- **Mode 4: General B2B Prospecting**
  - Focuses on businesses with verified phone numbers for direct cold-calling and sales outreach.

---

### 3. User Personas & Use Cases
- **Solo Freelancers & Agency Owners**: Need contact details for local service providers (e.g., dental clinics in Koramangala, gyms in Kushtia) for B2B outreach without paying $50-$200/mo for lead tools.
- **Sales Reps / Marketers**: Want ready-to-use Excel sheets with valid phone numbers and clean formatting.
- **Non-Technical Users**: Want a simple web interface (inputs, search button, live progress bar, table view, download button) without editing code.

---

### 4. Functional Requirements

#### 4.1. Input Specification
The search interface must accept:
1. **Country**: (e.g., India, Bangladesh, USA)
2. **City / District**: (e.g., Bangalore, Dhaka, Austin)
3. **Area / Neighborhood**: (e.g., Koramangala, Mirpur, Downtown)
4. **Business Category**: (e.g., Dental clinics, Restaurants, Gyms, Pet shops)
5. **Optional Keyword**: Additional search nuance (e.g., "vegetarian", "24 hours")
6. **Max Results Limit**: (e.g., 20, 50, 100)
7. **Filter - Require Phone**: Checkbox (Yes / No). If checked, exclude businesses without phone numbers.
8. **Filter - Require Website**: Checkbox (Yes / No). If checked, exclude businesses without websites.

#### 4.2. Business Discovery & Data Extraction
The agent queries the active provider (OpenStreetMap Overpass API by default) and extracts:
- **Business Name**: Cleaned commercial name
- **Phone**: Primary contact phone / mobile number
- **Address**: Street, suburb, city, postcode
- **Website**: Official website or social page URL
- **Maps Link**: Direct OpenStreetMap or Google Maps URL
- **Category**: Primary business category / amenity tag
- **Coordinates**: Latitude and Longitude
- **Source**: Data origin (e.g., `OpenStreetMap`, `Google Places`)
- **Status**: Verification state (`FOUND`, `MISSING_PHONE`, `MISSING_WEBSITE`)

#### 4.3. Data Quality, Normalization & Deduplication
- **Deduplication**: Match businesses by name similarity (fuzzy matching/token set) and geographical proximity (within ~150 meters).
- **Phone Normalization**: Strip invalid symbols, spaces, formatting quirks; format to local/international standard where possible.
- **URL Normalization**: Ensure proper `http://` or `https://` prefix, lowercase domain, strip tracking query parameters.
- **Whitespace Sanitization**: Trim excessive whitespace, strip HTML tags.

#### 4.4. Live Progress Tracking
The user interface must provide real-time status updates without freezing the browser:
- `Step 1/6`: Geocoding area coordinates (Nominatim)
- `Step 2/6`: Querying Overpass API for POIs
- `Step 3/6`: Extracting contact details and tags
- `Step 4/6`: Normalizing and deduplicating records
- `Step 5/6`: Filtering (e.g., applying "Must have phone" requirement)
- `Step 6/6`: Ready for export (`X leads found, Y filtered out`)

#### 4.5. Results Table & Interactive Controls
- Interactive, paginated table with sortable columns.
- One-click copy phone number.
- Direct links to open website or map location in a new tab.
- Ability to delete unwanted individual leads from the results list before exporting.
- Search/filter box within results table.

#### 4.6. Export Functionality
- **Excel (.xlsx)**: Formatted table with auto-adjusted column widths, bold headers, and freeze header row.
  - Columns: `Business Name`, `Phone`, `Address`, `Website`, `Maps Link`, `Category`, `Source`
  - Filename format: `{category}_{area}_{city}_{YYYY-MM-DD}.xlsx`
- **CSV (.csv)**: UTF-8 encoded comma-separated file with identical columns.

---

### 5. Non-Functional Requirements
- **Runtime Performance**: Geocoding and query execution should complete within 5–15 seconds for typical queries (up to 100 leads).
- **Graceful Error Handling**: Clear, friendly error messages if a location cannot be resolved, if rate limits occur, or if zero businesses match the criteria. No raw 500 error dumps.
- **Zero-Persistence / Ephemeral Compliance**: Render Free web services have ephemeral storage; Excel and CSV files must be streamed directly to the browser for download without relying on persistent local disk storage.
- **Responsible Use & Anti-Spam Disclaimer**: Prominently display legal notice regarding TRAI DND, TCPA, GDPR, and anti-spam compliance.

---

### 6. Out of Scope (Phase 1 MVP)
- Direct unauthorized Google Maps HTML web scraping (violates ToS, triggers IP bans).
- Paid proxy rotation networks or paid CAPTCHA solvers.
- Automated bulk cold emailing or automated WhatsApp messaging directly from the app (can be planned for Phase 2).
- Paid databases (Supabase paid tiers, AWS RDS).
