# 📍 LeadFinder Free: Local Business Lead Generation Agent

A lightweight, 100% free web application and AI agent designed to discover local business leads, collect publicly available contact information (Name, Phone, Address, Website, Maps Link), clean and deduplicate the data, and export directly into clean **Excel (`.xlsx`)** and **CSV (`.csv`)** files.

Built strictly under a **$0/month** architecture constraint with no required paid APIs, credit cards, or paid databases.

---

## 🚀 Key Features

- **100% Free Default Provider**: Queries OpenStreetMap via Overpass API and Nominatim. No API keys or credit cards needed.
- **Provider Abstraction**: Architecture supports plug-and-play providers. Optional official Google Places API (New) integration if you provide an API key.
- **Data Quality & Anti-Hallucination**:
  - Normalizes phone numbers (E.164 and local standard).
  - Sanitizes website URLs and removes tracking queries.
  - Deduplicates by coordinate proximity (<150m) and fuzzy name similarity.
  - Zero synthetic or fabricated data: missing fields remain empty.
  - Spreadsheet formula injection protection (protects Excel against malicious payloads).
- **Interactive UI**:
  - Live progress tracking without browser freeze.
  - Responsive metric cards (Discovered POIs, Matching Leads, Verified Phones).
  - Searchable and sortable results table.
  - Direct 1-click in-memory download of styled **Excel (`.xlsx`)** and **CSV (`.csv`)**.
- **Ephemeral-Ready**: Runs completely in memory, making it 100% compatible with Render's free tier ephemeral filesystem.

---

## 🤖 Multi-Agent Team Structure

This project is architected by 6 specialized AI agent personas (see [`team_agents.md`](file:///E:/Projects/google-search-to-exel/team_agents.md)):

1. **Project Manager Agent** (`manager_agent`): Enforces the $0/month budget rule, validates PRD compliance, and signs off on milestones.
2. **Pipeline Orchestrator Agent** (`orchestrator_agent`): Manages the linear event flow from geocoding to data provider, normalization, and export.
3. **Smart Reasoning Thinker** (`smart_thinker_agent`): Implements spatial math (radial bounding boxes), category synonym mapping, and fuzzy deduplication.
4. **Senior Programmer Agent** (`programmer_agent`): Writes clean, modular Python codebase, providers, models, and export engines.
5. **UI/UX Specialist Agent** (`ui_ux_agent`): Crafts the modern Streamlit interface, live progress indicators, and interactive tables.
6. **Hosting & DevOps Expert** (`hosting_expert_agent`): Configures Render free-tier deployment, Dockerfile, healthchecks, and ephemeral file streaming.

---

## 📁 Project Structure

```
google-search-to-exel/
├── .env.example              # Environment variables template
├── .gitignore                # Git exclusions (protects secrets and artifacts)
├── Dockerfile                # Multi-stage production container for Render
├── render.yaml               # 1-click Render blueprint specification
├── requirements.txt          # Python dependencies
├── app.py                    # Streamlit web dashboard entrypoint
├── PRD.md                    # Product Requirements Document
├── architecture.md           # System architecture & sequence diagrams
├── agent.md                  # AI agent specifications & tool definitions
├── context.md                # Event triggers, token budgets & state machine
├── team_agents.md            # Multi-agent roles & collaboration rules
├── skills/                   # Automated agent skill playbooks
│   ├── review_skill.md       # Quality audit & anti-hallucination checks
│   ├── recover_skill.md      # Auto-failover & radial fallback strategy
│   └── data_validation_skill.md # Schema invariants & sanitization
├── src/
│   ├── config.py             # Config & endpoint mirror list
│   ├── models.py             # Dataclasses (Lead, SearchParams, GeoLocation)
│   ├── providers/            # Pluggable data providers
│   │   ├── base.py           # BusinessDataProvider interface
│   │   ├── osm_provider.py   # 100% Free OpenStreetMap Overpass provider
│   │   └── google_provider.py# Optional Google Places provider
│   ├── services/             # Core business logic services
│   │   ├── geocoding.py      # Nominatim geocoder with radial fallback
│   │   ├── normalizer.py     # Phone, URL, and address sanitization
│   │   ├── deduplicator.py   # Proximity and fuzzy name deduplicator
│   │   ├── exporter.py       # Styled in-memory Excel and CSV generator
│   │   └── synonym_mapper.py # Business category to OSM tag mapping
│   ├── pipelines/            # Pipeline orchestrators
│   │   └── lead_pipeline.py  # Coordinates search, filter, and progress
│   └── ui/                   # UI components
│       └── components.py     # Metric cards, custom styling, DataFrames
└── tests/                    # Automated test suites
    ├── test_pipeline.py      # Bangalore restaurants pipeline test
    └── test_kushtia.py       # Secondary location and fallback test
```

---

## 💻 Local Quickstart

### Prerequisites
- Python 3.10+ (or Python 3.14)
- Git

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/your-username/google-search-to-exel.git
cd google-search-to-exel

# Optional: Create virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
```bash
cp .env.example .env
```
*Note: The app runs 100% free via OpenStreetMap without any changes to `.env`.*

### 3. Run the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🌐 Deploying to Render for 100% Free

### Method 1: Using `render.yaml` (Recommended Blueprint)
1. Push your repository to **GitHub**.
2. Go to [Render Dashboard](https://dashboard.render.com).
3. Click **New +** ➔ **Blueprint**.
4. Connect your GitHub repository.
5. Render reads `render.yaml` and launches the Free Web Service automatically!

### Method 2: Manual Web Service
1. In Render, select **New +** ➔ **Web Service**.
2. Connect your repo and set:
   - **Environment**: `Python` (or `Docker`)
   - **Plan**: `Free`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
3. Click **Create Web Service**. Your free app will be live with an SSL URL (`https://your-app.onrender.com`).

---

## ⚖️ Responsible Use & Legal Notice

This application queries publicly available data for legitimate business inquiries and B2B prospecting.
- Respect local communication standards including **India's TRAI DND registry**, the **European GDPR**, and the **US TCPA**.
- Do not use exported records for unauthorized mass spam.
- Comply with OpenStreetMap's [Acceptable Use Policy](https://operations.osmfoundation.org/policies/nominatim/).
