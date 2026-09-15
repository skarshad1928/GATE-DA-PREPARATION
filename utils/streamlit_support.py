from __future__ import annotations

import streamlit as st

from ai.config import get_settings
from ai.gemini_client import GeminiQuestionService
from database.mongodb import MongoQuestionRepository
from utils.csv_logger import CsvAttemptLogger


@st.cache_resource(show_spinner=False)
def get_services() -> dict:
    settings = get_settings()
    repository = MongoQuestionRepository(settings=settings)
    if repository.is_configured():
        try:
            repository.ensure_indexes()
        except Exception:
            pass

    return {
        "settings": settings,
        "gemini": GeminiQuestionService(settings=settings),
        "repository": repository,
        "csv_logger": CsvAttemptLogger(settings.attempt_log),
    }


def apply_brand_styles() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

            :root {
                --bg-deep: #060a14;
                --bg-panel: #0d1424;
                --bg-panel-soft: rgba(17, 25, 43, 0.72);
                --line-soft: rgba(120, 170, 255, 0.14);
                --ink: #e7edf7;
                --ink-dim: #94a3c2;
                --accent-cyan: #21e6c1;
                --accent-violet: #8b6bff;
                --accent-amber: #ffb454;
                --accent-rose: #ff5d7a;
            }

            html, body, [class*="css"] {
                font-family: 'Space Grotesk', 'Segoe UI', sans-serif;
            }

            .stApp {
                background:
                    radial-gradient(circle at 8% 0%, rgba(139, 107, 255, 0.20), transparent 32%),
                    radial-gradient(circle at 92% 8%, rgba(33, 230, 193, 0.14), transparent 30%),
                    radial-gradient(circle at 50% 100%, rgba(255, 93, 122, 0.08), transparent 40%),
                    linear-gradient(180deg, #060a14 0%, #0a0f1e 55%, #060a14 100%);
                color: var(--ink);
            }

            section[data-testid="stSidebar"] {
                background: linear-gradient(180deg, #0a0f1e 0%, #070b16 100%);
                border-right: 1px solid var(--line-soft);
            }

            /* Section badge strip -- reinforces "every section matters equally" */
            .syllabus-strip {
                display: flex;
                flex-wrap: wrap;
                gap: 0.5rem;
                margin: 0.75rem 0 1.25rem 0;
            }
            .syllabus-chip {
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.74rem;
                letter-spacing: 0.02em;
                padding: 0.42rem 0.75rem;
                border-radius: 10px;
                border: 1px solid var(--line-soft);
                background: rgba(255, 255, 255, 0.03);
                color: var(--ink-dim);
            }
            .syllabus-chip.active {
                color: #06110d;
                background: linear-gradient(120deg, var(--accent-cyan), #7ef7dc);
                border-color: transparent;
                font-weight: 600;
            }

            .hero-panel {
                position: relative;
                background: linear-gradient(155deg, rgba(139, 107, 255, 0.16), rgba(33, 230, 193, 0.08));
                border: 1px solid var(--line-soft);
                border-radius: 20px;
                padding: 1.6rem 1.8rem;
                box-shadow: 0 30px 60px rgba(3, 6, 14, 0.55);
                overflow: hidden;
            }
            .hero-panel::before {
                content: "";
                position: absolute;
                inset: 0;
                background-image: radial-gradient(rgba(255,255,255,0.06) 1px, transparent 1px);
                background-size: 22px 22px;
                opacity: 0.5;
                pointer-events: none;
            }
            .hero-eyebrow {
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.78rem;
                letter-spacing: 0.16em;
                text-transform: uppercase;
                color: var(--accent-cyan);
                margin-bottom: 0.6rem;
            }
            .hero-title {
                font-size: 2.35rem;
                font-weight: 700;
                letter-spacing: -0.03em;
                margin-bottom: 0.55rem;
                background: linear-gradient(120deg, #ffffff 30%, var(--accent-cyan) 100%);
                -webkit-background-clip: text;
                background-clip: text;
                color: transparent;
            }
            .hero-subtitle {
                color: var(--ink-dim);
                font-size: 1.02rem;
                line-height: 1.65;
                max-width: 62ch;
            }

            .metric-panel, .section-card {
                background: var(--bg-panel-soft);
                border: 1px solid var(--line-soft);
                border-radius: 16px;
                padding: 1.1rem 1.3rem;
                box-shadow: 0 18px 40px rgba(3, 6, 14, 0.35);
                backdrop-filter: blur(8px);
            }
            .metric-panel h4, .section-card h4 {
                margin: 0 0 0.4rem 0;
                font-size: 1.02rem;
                color: var(--ink);
            }
            .metric-panel p, .section-card p {
                margin: 0;
                color: var(--ink-dim);
                font-size: 0.92rem;
                line-height: 1.55;
            }

            .section-card {
                border-left: 3px solid var(--accent-violet);
            }
            .section-card .section-number {
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.75rem;
                color: var(--accent-violet);
                letter-spacing: 0.08em;
            }

            .topic-chip {
                display: inline-block;
                margin: 0.2rem 0.35rem 0.2rem 0;
                padding: 0.4rem 0.75rem;
                border-radius: 999px;
                background: rgba(33, 230, 193, 0.10);
                color: var(--accent-cyan);
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.82rem;
                border: 1px solid rgba(33, 230, 193, 0.25);
            }

            div[data-testid="stMetric"] {
                background: var(--bg-panel-soft);
                border: 1px solid var(--line-soft);
                border-radius: 14px;
                padding: 0.7rem 0.9rem;
            }
            div[data-testid="stMetricLabel"] {
                color: var(--ink-dim) !important;
            }
            div[data-testid="stMetricValue"] {
                color: var(--ink) !important;
                font-family: 'JetBrains Mono', monospace;
            }

            .stButton > button, .stDownloadButton > button {
                background: linear-gradient(120deg, var(--accent-violet), var(--accent-cyan));
                color: #060a14;
                font-weight: 600;
                border: none;
                border-radius: 10px;
            }
            .stButton > button:hover, .stDownloadButton > button:hover {
                filter: brightness(1.08);
                color: #060a14;
            }

            h1, h2, h3 { color: var(--ink); letter-spacing: -0.01em; }
            .stCaption, .stMarkdown p { color: var(--ink-dim); }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_status_strip(settings, gemini, repository) -> None:
    cols = st.columns(3)
    cols[0].metric("Gemini Model", settings.gemini_model)
    cols[1].metric("Gemini Ready", "Yes" if gemini.is_configured() else "No")
    cols[2].metric("Mongo Ready", "Yes" if repository.is_available() else "No")


def render_syllabus_strip(active_key: str | None = None) -> None:
    """Show all 7 GATE DA syllabus sections as a strip, highlighting the active one.

    This is a visual reminder that every section carries equal weight in the
    exam, not just the one the user happens to be practicing right now.
    """
    from utils.helpers import PRACTICE_BLUEPRINTS, SECTION_ORDER

    chips = []
    for index, key in enumerate(SECTION_ORDER, start=1):
        title = PRACTICE_BLUEPRINTS[key]["title"]
        css_class = "syllabus-chip active" if key == active_key else "syllabus-chip"
        chips.append(f'<span class="{css_class}">{index:02d} · {title}</span>')
    st.markdown(f'<div class="syllabus-strip">{"".join(chips)}</div>', unsafe_allow_html=True)
