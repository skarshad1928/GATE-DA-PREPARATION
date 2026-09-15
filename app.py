from __future__ import annotations

import streamlit as st

from utils.helpers import PRACTICE_BLUEPRINTS, SECTION_ORDER
from utils.streamlit_support import apply_brand_styles, get_services, render_status_strip, render_syllabus_strip


st.set_page_config(
    page_title="GATE DA Prep Hub",
    page_icon="🧬",
    layout="wide",
)

apply_brand_styles()
services = get_services()
settings = services["settings"]
gemini = services["gemini"]
repository = services["repository"]

render_syllabus_strip()

st.markdown(
    """
    <div class="hero-panel">
        <div class="hero-eyebrow">GATE 2027 · IIT Madras · Data Science & Artificial Intelligence</div>
        <div class="hero-title">GATE DA Prep Hub</div>
        <div class="hero-subtitle">
            An adaptive Streamlit + Gemini workspace built directly from the official GATE DA
            syllabus. All seven sections — Probability & Statistics, Linear Algebra, Calculus &
            Optimization, Programming/DSA, Database Management & Warehousing, Machine Learning,
            and AI — get equal footing. Generate original questions, track performance per
            section, and sharpen exactly what the paper tests.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

render_status_strip(settings, gemini, repository)

st.subheader("Launch a Section")
page_map = [
    ("Probability & Statistics", "pages/prob_stats.py"),
    ("Linear Algebra", "pages/linear_algebra.py"),
    ("Calculus & Optimization", "pages/calculus_optimization.py"),
    ("Programming, DSA", "pages/programming_dsa.py"),
    ("Database Mgmt & Warehousing", "pages/dbms.py"),
    ("Machine Learning", "pages/machine_learning.py"),
    ("Artificial Intelligence", "pages/artificial_intelligence.py"),
]
row1 = st.columns(4)
row2 = st.columns(4)
for column, (label, target) in zip(row1 + row2, page_map):
    column.page_link(target, label=label, use_container_width=True)
row2[3].page_link("pages/dashboard.py", label="Dashboard", use_container_width=True)

st.subheader("Platform Capabilities")
feature_cols = st.columns(3)
feature_cols[0].markdown(
    """
    <div class="metric-panel">
        <h4>Syllabus-Locked Generation</h4>
        <p>Every prompt is scoped to the exact section and topic from the GATE DA syllabus PDF — nothing off-syllabus sneaks in.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
feature_cols[1].markdown(
    """
    <div class="metric-panel">
        <h4>Adaptive Difficulty</h4>
        <p>Difficulty shifts upward after strong performance and eases back when accuracy drops below target, per section.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
feature_cols[2].markdown(
    """
    <div class="metric-panel">
        <h4>Persistent Insights</h4>
        <p>Attempts can be stored in MongoDB and mirrored to local CSV logs, broken down by section and topic.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("All 7 Syllabus Sections")
st.caption("No section is optional — the layout below mirrors the syllabus PDF's own numbering.")
section_cols = st.columns(2)
for index, key in enumerate(SECTION_ORDER):
    blueprint = PRACTICE_BLUEPRINTS[key]
    column = section_cols[index % 2]
    column.markdown(
        f"""
        <div class="section-card">
            <div class="section-number">SECTION {index + 1:02d}</div>
            <h4>{blueprint["title"]}</h4>
            <p>{blueprint["summary"]}</p>
        </div>
        <div style="height: 0.6rem;"></div>
        """,
        unsafe_allow_html=True,
    )
