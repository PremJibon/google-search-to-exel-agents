"""
Responsive Stylesheet — Omnichannel Mobile, Tablet, and Desktop Adaptive Layouts
Engineered for Streamlit SaaS interfaces to guarantee pixel-perfect responsiveness:
- Mobile Phones (320px - 480px)
- Tablets & Phablets (768px - 1024px)
- Laptops, Desktops & 4K Ultra-Wide Monitors (1200px+)
"""

import streamlit as st

def inject_responsive_saas_styles():
    """Injects comprehensive responsive CSS, prevents font overlaps, and preserves icon ligatures."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        /* Safe Typography - Explicitly do NOT overwrite Streamlit icon ligatures */
        html, body, p, span.st-emotion-cache-p, .stMarkdown, .saas-hero, .metric-card, 
        .chat-bubble-agent, .chat-bubble-user, div.stButton > button, div.stSelectbox, 
        div.stTextInput, div.stNumberInput, div.stTextArea {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            -webkit-tap-highlight-color: transparent;
        }

        /* Enforce native Material Symbols & Streamlit icon glyphs */
        [data-testid="stIconMaterial"], 
        .material-symbols-rounded, 
        .material-icons,
        [data-testid*="Icon"],
        [class*="stIcon"] {
            font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
            font-style: normal !important;
            font-weight: normal !important;
            letter-spacing: normal !important;
            text-transform: none !important;
            display: inline-block !important;
            white-space: nowrap !important;
            word-wrap: normal !important;
            direction: ltr !important;
        }

        /* Container Fluid Constraints for Desktop & Ultra-Wide */
        .main .block-container {
            max-width: 1380px !important;
            padding-top: 1.6rem !important;
            padding-bottom: 3.5rem !important;
            transition: all 0.2s ease-in-out;
        }

        /* Responsive Hero Header */
        .saas-hero {
            background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F172A 100%);
            border: 1px solid #334155;
            border-radius: 14px;
            padding: clamp(0.9rem, 2.5vw, 1.6rem);
            margin-bottom: 1.2rem;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.35);
            overflow: hidden;
        }
        .saas-title {
            font-size: clamp(1.3rem, 3.5vw, 2.1rem);
            font-weight: 800;
            background: linear-gradient(90deg, #38BDF8 0%, #818CF8 50%, #C084FC 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.35rem;
            letter-spacing: -0.02em;
            line-height: 1.3;
            display: block;
            word-break: break-word;
        }
        .saas-subtitle {
            font-size: clamp(0.82rem, 1.8vw, 0.98rem);
            color: #94A3B8;
            font-weight: 400;
            line-height: 1.5;
            margin-bottom: 0.5rem;
            display: block;
        }

        /* Touch-Friendly Agent Badges */
        .agent-pills-wrap {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 8px;
        }
        .agent-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: clamp(0.72rem, 1.8vw, 0.78rem);
            font-weight: 600;
            white-space: nowrap;
        }
        .pill-nova { background: rgba(16, 185, 129, 0.15); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.35); }
        .pill-max { background: rgba(59, 130, 246, 0.15); color: #3B82F6; border: 1px solid rgba(59, 130, 246, 0.35); }
        .pill-apex { background: rgba(239, 68, 68, 0.15); color: #EF4444; border: 1px solid rgba(239, 68, 68, 0.35); }
        .pill-atlas { background: rgba(168, 85, 247, 0.15); color: #A855F7; border: 1px solid rgba(168, 85, 247, 0.35); }

        /* Adaptive Responsive Metric Cards Grid */
        .responsive-metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
            gap: 10px;
            width: 100%;
            margin: 12px 0 16px 0;
        }
        .metric-card {
            background: linear-gradient(180deg, #1E293B 0%, #0F172A 100%);
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 0.8rem 0.5rem;
            text-align: center;
            box-shadow: 0 4px 8px -2px rgba(0, 0, 0, 0.25);
            transition: transform 0.2s ease, border-color 0.2s ease;
            overflow: hidden;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            border-color: #64748B;
        }
        .metric-value {
            font-size: clamp(1.3rem, 3vw, 1.8rem);
            font-weight: 800;
            color: #F8FAFC;
            letter-spacing: -0.02em;
            line-height: 1.2;
            margin-bottom: 4px;
        }
        .metric-label {
            font-size: clamp(0.68rem, 1.6vw, 0.76rem);
            color: #94A3B8;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            line-height: 1.25;
            word-break: break-word;
            overflow-wrap: break-word;
        }

        /* Touch-Optimized Tabs Navigation */
        [data-baseweb="tab-list"] {
            overflow-x: auto !important;
            flex-wrap: nowrap !important;
            -webkit-overflow-scrolling: touch !important;
            scrollbar-width: thin;
            padding-bottom: 6px;
            gap: 8px;
        }
        [data-baseweb="tab"] {
            min-height: 42px !important;
            padding: 8px 14px !important;
            font-size: clamp(0.82rem, 1.8vw, 0.92rem) !important;
            font-weight: 600 !important;
            white-space: nowrap !important;
            border-radius: 8px 8px 0 0 !important;
        }

        /* Touch Target Ergonomics: Buttons & Selects */
        div.stButton > button {
            min-height: 42px !important;
            padding: 0.6rem 1.1rem !important;
            font-size: 0.92rem !important;
            border-radius: 8px !important;
            line-height: 1.3 !important;
        }

        /* Chatroom Bubble Responsive Styling */
        .chat-bubble-agent {
            background: #1E293B;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: clamp(0.8rem, 2.5vw, 1.2rem);
            margin-bottom: 0.9rem;
            color: #F1F5F9;
            line-height: 1.55;
            word-wrap: break-word;
        }
        .chat-bubble-user {
            background: #0284C7;
            border-radius: 12px;
            padding: clamp(0.7rem, 2vw, 1.0rem);
            margin-bottom: 0.9rem;
            color: #FFFFFF;
            margin-left: 10%;
            word-wrap: break-word;
            line-height: 1.5;
        }

        /* Voice Card Widget Styling */
        .voice-card-container {
            background: #0F172A;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 12px 16px;
            margin: 10px 0 14px 0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.25);
        }
        .voice-card-title {
            font-size: 13px;
            font-weight: 700;
            color: #38BDF8;
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .voice-result-box {
            background: #1E293B;
            border-left: 3px solid #10B981;
            border-radius: 6px;
            padding: 10px 14px;
            margin-top: 8px;
            font-size: 13px;
            color: #F1F5F9;
            line-height: 1.4;
        }

        /* WhatsApp Direct Trigger Button */
        .wa-chat-link {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: #25D366;
            color: white !important;
            padding: 6px 14px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 13px;
            text-decoration: none;
            margin: 6px 4px 6px 0;
            transition: background 0.2s ease;
        }
        .wa-chat-link:hover {
            background: #1EBE5D;
            color: white !important;
        }

        /* ========================================================
           📱 MOBILE PHONES BREAKPOINT (<= 768px)
           ======================================================== */
        @media screen and (max-width: 768px) {
            .main .block-container {
                padding-left: 0.65rem !important;
                padding-right: 0.65rem !important;
                padding-top: 1.0rem !important;
            }
            .saas-hero {
                padding: 0.9rem 0.8rem !important;
                border-radius: 10px !important;
            }
            .agent-pills-wrap {
                gap: 4px;
            }
            .agent-pill {
                padding: 3px 8px;
                font-size: 0.72rem;
            }
            /* Stack ONLY form filter blocks so inputs don't squeeze */
            .stForm [data-testid="stHorizontalBlock"] > div[data-testid="column"] {
                min-width: 100% !important;
                flex: 1 1 100% !important;
                margin-bottom: 0.4rem;
            }
            /* 2-Column Grid for Metrics on Mobile */
            .responsive-metrics-grid {
                grid-template-columns: repeat(2, 1fr) !important;
                gap: 8px !important;
            }
            /* Chat bubble full width on mobile */
            .chat-bubble-user {
                margin-left: 4% !important;
            }
            /* Map container height clamp on mobile */
            iframe[title*="map"], iframe[id*="map"] {
                height: 400px !important;
            }
        }

        /* ========================================================
           📱 VERY SMALL SCREENS (<= 400px - iPhone SE, compact)
           ======================================================== */
        @media screen and (max-width: 400px) {
            .responsive-metrics-grid {
                grid-template-columns: 1fr !important;
            }
            .saas-title {
                font-size: 1.25rem !important;
            }
        }

        /* ========================================================
           💻 TABLETS BREAKPOINT (769px to 1024px)
           ======================================================== */
        @media screen and (min-width: 769px) and (max-width: 1024px) {
            .main .block-container {
                padding-left: 1.2rem !important;
                padding-right: 1.2rem !important;
            }
            .responsive-metrics-grid {
                grid-template-columns: repeat(3, 1fr) !important;
            }
        }

        /* ========================================================
           🖥️ LARGE SCREENS & DESKTOP (>= 1025px)
           ======================================================== */
        @media screen and (min-width: 1025px) {
            .responsive-metrics-grid {
                grid-template-columns: repeat(5, 1fr) !important;
            }
        }
        </style>
    """, unsafe_allow_html=True)
