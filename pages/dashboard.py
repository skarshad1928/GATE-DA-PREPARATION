from __future__ import annotations

import streamlit as st

from utils.helpers import PRACTICE_BLUEPRINTS, SECTION_ORDER, summarize_attempts
from utils.streamlit_support import apply_brand_styles, get_services, render_syllabus_strip


def _to_frame(rows):
    try:
        import pandas as pd

        return pd.DataFrame(rows)
    except Exception:
        return rows


st.set_page_config(page_title="GATE DA Prep Hub | Dashboard", page_icon="📊", layout="wide")
apply_brand_styles()
services = get_services()
repository = services["repository"]
csv_logger = services["csv_logger"]

attempts = []
if repository.is_available():
    try:
        attempts = repository.list_recent_attempts(limit=250)
    except Exception:
        attempts = []
if not attempts:
    attempts = csv_logger.load_attempts(limit=250)

summary = summarize_attempts(attempts)

render_syllabus_strip()

st.markdown(
    """
    <div class="hero-panel">
        <div class="hero-eyebrow">GATE 2027 · Data Science & AI</div>
        <div class="hero-title">Performance Dashboard</div>
        <div class="hero-subtitle">
            Review how accuracy, time spent, and topic-level strengths are evolving across your
            recent practice history, across all seven syllabus sections.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

metric_cols = st.columns(4)
metric_cols[0].metric("Total Attempts", summary["attempts"])
metric_cols[1].metric("Overall Accuracy", f'{summary["accuracy"]:.1f}%')
metric_cols[2].metric("Average Time", f'{summary["average_time_seconds"]:.0f}s')
metric_cols[3].metric("Weak Topics", len(summary["weak_topics"]))

if not attempts:
    st.info("No attempts recorded yet. Generate and solve a few questions to populate this dashboard.")
else:
    st.subheader("Section Coverage")
    section_names = {key: PRACTICE_BLUEPRINTS[key]["section_name"] for key in SECTION_ORDER}
    section_counts = {name: 0 for name in section_names.values()}
    for item in attempts:
        section = item.get("section")
        if section in section_counts:
            section_counts[section] += 1
    coverage_rows = [
        {"section": name, "attempts": section_counts[name]}
        for name in section_names.values()
    ]
    st.dataframe(_to_frame(coverage_rows), use_container_width=True)
    uncovered = [row["section"] for row in coverage_rows if row["attempts"] == 0]
    if uncovered:
        st.warning("No attempts yet in: " + ", ".join(uncovered))

    st.subheader("Topic Breakdown")
    st.dataframe(_to_frame(summary["topic_rows"]), use_container_width=True)

    st.subheader("Difficulty Breakdown")
    st.dataframe(_to_frame(summary["difficulty_rows"]), use_container_width=True)

    recent_rows = [
        {
            "date": item.get("date"),
            "section": item.get("section"),
            "topic": item.get("topic"),
            "difficulty": item.get("difficulty"),
            "selected": item.get("my_answer"),
            "correct": item.get("correct_answer"),
            "is_correct": item.get("is_correct"),
            "time_taken_seconds": item.get("time_taken_seconds"),
        }
        for item in attempts[:15]
    ]
    st.subheader("Recent Attempts")
    st.dataframe(_to_frame(recent_rows), use_container_width=True)
