# 📍 LeadFinder Agency Co-Pilot (v2.1)

A modern, 100% free-first SaaS platform and autonomous Multi-Agent AI team designed to discover local business leads, perform digital presence audits, and craft high-converting agency sales pitches and client acquisition campaigns.

Export sales-ready leads with custom outreach angles directly into formatted **Excel (`.xlsx`)** and **CSV (`.csv`)** files.

Built strictly under a **$0/month** architecture constraint with no paid APIs or credit cards required.

---

## 🚀 Key Features

- **⚡ Groq Ultra-Fast LPU Engine (Primary Brain)**: Powered by Groq's high-speed inference (`openai/gpt-oss-120b`, `qwen/qwen3.8-27b`) delivering razor-sharp agency copy in under 500 milliseconds.
- **🤝 Collaborative Dual-Agent Handshake Loop**:
  - **Nova (Scout)** discovers local businesses.
  - **Max (Auditor)** audits digital assets and flags businesses needing websites or booking bots.
  - **Nova & Max Co-Pilot** immediately triggers **Deep Web Search (Tavily)** to uncover missing websites, social profiles, and phone numbers in real-time.
  - **Apex (Digital Marketer)** synthesizes tailored cold outreach campaigns.
- **💬 Interactive Multi-Agent Agency Chatroom**:
  - Live conversation with **Apex**, **Nova**, **Max**, and **Atlas**.
  - Context-aware: Agents directly reference the currently loaded leads to write custom WhatsApp pitches, email sequences, retainer pricing, and objection scripts.
- **🛡️ Bulletproof Security Shield**:
  - **Zero-Trust Passkey Gate**: Enforces a master passkey (`APP_ACCESS_PASSWORD`) protecting the dashboard against unauthorized access and bot scraping.
  - **Automated Output Redaction Filter**: Real-time regex scanner redacts any API tokens or keys before output reaches the browser.
  - **CSV / Spreadsheet Formula Injection Defense**: Neutralizes `=CMD()`, `@SUM`, `+`, `-`, `|` DDE triggers in exported files.
  - **Rate-Limiting Cooldown & 100-Lead Ceiling**: Protects memory on 512 MB free tier instances from DoS crashes.
- **🎨 Modern SaaS Design**:
  - Cascading dropdowns for Country (🇧🇩 Bangladesh, 🇮🇳 India, 🇺🇸 USA, 🇬🇧 UK, etc.), dynamic Cities, and Neighborhoods.
  - Preset Category selectors with icons (Gyms, Dental Clinics, Restaurants, Salons, Auto Repair, etc.).
  - Glassmorphic dark styling, responsive KPI metric cards, and interactive geocoded map.

---

## 🤖 The Named AI Agency Team

| Agent | Avatar | Title | In-House Agency Role |
| :--- | :---: | :--- | :--- |
| **Nova** | 🔭 | **Lead Discovery Specialist** | Manages boundary geocoding, queries OpenStreetMap / Serper, and executes deep web enrichment. |
| **Max** | 🔍 | **Technical & Digital Auditor** | Audits websites, SSL status, social-only pages, and booking friction; assigns opportunity scores. |
| **Apex** | 📢 | **Digital Marketing Expert** | **Your agency's growth marketer & closer**. Writes cold WhatsApp scripts, 3-step email sequences, retainer pricing, and objection rebuttals. |
| **Atlas** | 🧭 | **Agency Growth Strategist** | Mentors high-ticket agency operations, 7-day client closing workflows, retainer packaging, and ROI guarantees. |

---

## 📁 Project Structure

```
google-search-to-exel/
├── .dockerignore             # Excludes secrets from container builds
├── .env.example              # Environment variables template
├── .gitignore                # Protects secrets from git tracking
├── Dockerfile                # Hardened container with anti-XSRF defense
├── render.yaml               # 1-click Render blueprint specification
├── requirements.txt          # Python dependencies
├── app.py                    # Streamlit SaaS web application & chatroom
├── PRD.md                    # Product Requirements Document
├── architecture.md           # System architecture & sequence diagrams
├── agent.md                  # AI agent specifications & tool definitions
├── context.md                # Event triggers, token budgets & state machine
├── team_agents.md            # Multi-agent roles & collaboration rules
├── skills/                   # Automated agent skill playbooks
├── src/
│   ├── config.py             # Config & endpoint mirrors
│   ├── models.py             # Dataclasses (Lead, SearchParams, GeoLocation)
│   ├── providers/            # Pluggable data providers (OSM, Serper, Tavily)
│   ├── services/
│   │   ├── security.py       # Passkey gate, secret redaction & rate limiting
│   │   ├── llm_helper.py     # Multi-LLM Gateway (Groq, BazaarLink, OpenRouter)
│   │   ├── agent_chat.py     # Named agent personalities & chat engine
│   │   ├── geocoding.py      # Nominatim geocoder with radial fallback
│   │   ├── normalizer.py     # Phone E.164, URL & formula injection sanitizers
│   │   ├── deduplicator.py   # Proximity and fuzzy name deduplicator
│   │   └── exporter.py       # Styled in-memory Excel and CSV generator
│   └── ui/
│       └── components.py     # Modern SaaS styling & cascading location presets
└── tests/
    ├── test_security_suite.py# 5-layer security verification tests
    ├── test_agent_system.py  # Dual-loop pipeline and multi-agent chat tests
    └── test_pipeline.py      # Core data retrieval tests
```

---

## 💻 Local Quickstart

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/your-username/google-search-to-exel.git
cd google-search-to-exel

# Create & activate virtual environment (optional)
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
```bash
cp .env.example .env
```
Add your free API keys in `.env`:
- `GROQ_API_KEY`: Get a free key at [console.groq.com](https://console.groq.com/keys) (Ultra-fast LPU inference).
- `TAVILY_API_KEY`: Get a free key at [tavily.com](https://tavily.com) (Deep search & phone lookup).
- `APP_ACCESS_PASSWORD`: Set a private passkey to lock your portal (or leave empty for open local access).

### 3. Run the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🌐 100% Free Hosting Deployment Options

### Option 1: Streamlit Community Cloud ⭐ *(Recommended - Best & Fastest)*
1. Push your repository to **GitHub** (ensure `.env` is ignored by `.gitignore`).
2. Visit [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub (100% Free).
3. Click **New app** ➔ Select your repository, branch (`master` or `main`), and main file (`app.py`).
4. Click **Advanced settings** ➔ Paste your secrets into the **Secrets** box:
   ```toml
   GROQ_API_KEY = "gsk_..."
   TAVILY_API_KEY = "tvly-..."
   APP_ACCESS_PASSWORD = "your_secure_password"
   ```
5. Click **Deploy**. Your app is live with free SSL and **never goes to sleep**!

---

### Option 2: Render Free Web Service
1. In [dashboard.render.com](https://dashboard.render.com), click **New +** ➔ **Blueprint**.
2. Connect your GitHub repo. Render will read `render.yaml` automatically.
3. In the Web Service Environment Variables settings, add:
   - `GROQ_API_KEY`
   - `TAVILY_API_KEY`
   - `APP_ACCESS_PASSWORD`
4. Click **Apply**. Render will build the container with healthchecks enabled.

---

### Option 3: Hugging Face Spaces (16 GB Free RAM)
1. In [huggingface.co/spaces](https://huggingface.co/spaces), click **Create new Space**.
2. Select **Streamlit** SDK and **Free 16GB CPU** tier.
3. Push your repo or upload files.
4. Under **Settings ➔ Variables and Secrets**, add `GROQ_API_KEY` and `APP_ACCESS_PASSWORD`.

---

## ⚖️ Responsible Use & Legal Compliance

This application extracts publicly available business information for legitimate B2B prospecting.
- Comply with international communication standards (**TRAI DND in India**, **TCPA in the US**, and **GDPR in Europe**).
- Do not engage in automated spam.
- Comply with OpenStreetMap's [Acceptable Use Policy](https://operations.osmfoundation.org/policies/nominatim/).
