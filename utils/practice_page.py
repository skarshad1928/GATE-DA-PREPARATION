from __future__ import annotations

from typing import Any

import streamlit as st

from ai.models import QuestionGenerationRequest, QuestionRecord
from database.mongodb import DatabaseOperationError
from utils.helpers import (
    PRACTICE_BLUEPRINTS,
    build_recent_question_summaries,
    flatten_topics,
    get_prompt_bundle,
    recommend_difficulty,
    summarize_attempts,
)
from utils.timer import elapsed_seconds, start_timer

QUESTION_STYLE_OPTIONS = [
    "GATE PYQ Style",
    "Conceptual Deep-Dive",
    "Numerical / Computation Heavy",
    "Speed Round",
]


def render_practice_page(blueprint_key: str) -> None:
    from utils.streamlit_support import (
        apply_brand_styles,
        get_services,
        render_status_strip,
        render_syllabus_strip,
    )

    apply_brand_styles()
    services = get_services()
    settings = services["settings"]
    gemini = services["gemini"]
    repository = services["repository"]
    csv_logger = services["csv_logger"]

    blueprint = PRACTICE_BLUEPRINTS[blueprint_key]
    state_key = f"{blueprint_key}_practice_state"
    if state_key not in st.session_state:
        st.session_state[state_key] = {
            "session": 1,
            "question_number": 0,
            "current_question": None,
            "started_at": None,
        }
    state = st.session_state[state_key]

    attempts = _load_attempts(repository, csv_logger, blueprint["section_name"])
    summary = summarize_attempts(attempts)
    default_difficulty = recommend_difficulty(
        accuracy=summary["accuracy"],
        attempts=summary["attempts"],
        current_difficulty="Medium",
    )

    render_syllabus_strip(active_key=blueprint_key)

    st.markdown(
        f"""
        <div class="hero-panel">
            <div class="hero-eyebrow">GATE 2027 · Data Science & AI</div>
            <div class="hero-title">{blueprint["title"]}</div>
            <div class="hero-subtitle">{blueprint["summary"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_status_strip(settings, gemini, repository)
    _render_metrics(summary)

    with st.sidebar:
        st.subheader("Practice Controls")
        topic = st.selectbox("Topic", flatten_topics(blueprint["topic_groups"]))
        difficulty_mode = st.radio(
            "Difficulty Mode",
            options=["Adaptive", "Manual"],
            horizontal=True,
        )
        difficulty = (
            default_difficulty
            if difficulty_mode == "Adaptive"
            else st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1)
        )
        question_style = st.selectbox(
            "Question Style",
            options=QUESTION_STYLE_OPTIONS,
        )
        focus_tags = st.multiselect(
            "Focus Tags",
            options=blueprint["default_patterns"],
            default=blueprint["default_patterns"][:2],
        )
        generate_clicked = st.button("Generate Question", use_container_width=True)

    if generate_clicked:
        _generate_question(
            blueprint_key=blueprint_key,
            topic=topic,
            difficulty=difficulty,
            company_level=question_style,
            exam_patterns=focus_tags or blueprint["default_patterns"],
            summary=summary,
            state=state,
            settings=settings,
            gemini=gemini,
            repository=repository,
        )

    if state.get("current_question"):
        _render_question_card(state, repository, csv_logger)
    else:
        st.info("Pick a topic on the left and generate your first GATE DA-style question for this section.")


def _render_metrics(summary: dict[str, Any]) -> None:
    cols = st.columns(4)
    cols[0].metric("Attempts", summary["attempts"])
    cols[1].metric("Accuracy", f'{summary["accuracy"]:.1f}%')
    cols[2].metric("Avg Time", f'{summary["average_time_seconds"]:.0f}s')
    cols[3].metric("Strong Topics", len(summary["strong_topics"]))

    if summary["strong_topics"]:
        st.caption("Strong topics: " + ", ".join(summary["strong_topics"][:4]))
    if summary["weak_topics"]:
        st.caption("Weak topics: " + ", ".join(summary["weak_topics"][:4]))


def _generate_question(
    blueprint_key: str,
    topic: str,
    difficulty: str,
    company_level: str,
    exam_patterns: list[str],
    summary: dict[str, Any],
    state: dict[str, Any],
    settings,
    gemini,
    repository,
) -> None:
    if not gemini.is_configured():
        st.error("Gemini is not configured. Add `GEMINI_API_KEY` to your `.env` file.")
        return

    recent_questions = _load_recent_questions(repository, blueprint_key)
    request = QuestionGenerationRequest(
        section=PRACTICE_BLUEPRINTS[blueprint_key]["section_name"],
        topic=topic,
        difficulty=difficulty,
        session=int(state["session"]),
        question_number=int(state["question_number"]) + 1,
        exam_patterns=exam_patterns,
        company_level=company_level,
        recent_accuracy=summary["accuracy"] if summary["attempts"] else None,
        strong_topics=summary["strong_topics"],
        weak_topics=summary["weak_topics"],
        recent_question_summaries=build_recent_question_summaries(recent_questions),
    )

    with st.spinner("Generating an original GATE DA-style question..."):
        try:
            question = gemini.generate_question(
                request=request,
                prompt_bundle=get_prompt_bundle(settings, blueprint_key),
            )
            if repository.is_available():
                repository.save_generated_question(question)
        except Exception as exc:
            st.error(f"Unable to generate a question right now: {exc}")
            return

    state["question_number"] = question.question_number
    state["current_question"] = question.to_document()
    state["started_at"] = start_timer()
    st.session_state[f"answer_{question.question_id}"] = None
    st.rerun()


def _render_question_card(state: dict[str, Any], repository, csv_logger) -> None:
    question = QuestionRecord.from_document(state["current_question"])

    st.subheader(f"Question {question.question_number}: {question.topic}")
    st.caption(
        f"{question.section} | {question.subtopic} | {question.difficulty} | "
        f"Expected Time: {question.expected_time_seconds}s"
    )
    st.write(question.question)

    options = [f"{key}. {value}" for key, value in question.options.items()]
    selected_option = st.radio(
        "Choose your answer",
        options=options,
        index=None,
        key=f"answer_{question.question_id}",
        disabled=question.status == "attempted",
    )

    action_cols = st.columns(2)
    submit_clicked = action_cols[0].button(
        "Submit Answer",
        use_container_width=True,
        disabled=question.status == "attempted",
    )
    next_clicked = action_cols[1].button("Next Question", use_container_width=True)

    if submit_clicked:
        if not selected_option:
            st.warning("Choose an option before submitting.")
        else:
            option_key = selected_option.split(".", 1)[0].strip().upper()
            question.register_attempt(option_key, elapsed_seconds(state["started_at"]))
            state["current_question"] = question.to_document()
            try:
                if repository.is_available():
                    repository.update_attempt(question)
            except DatabaseOperationError as exc:
                st.warning(f"MongoDB update failed, but your progress is still stored locally: {exc}")
            csv_logger.log_attempt(question)
            st.rerun()

    if next_clicked:
        state["current_question"] = None
        state["started_at"] = None
        st.rerun()

    if question.status == "attempted":
        _render_feedback(question)


def _render_feedback(question: QuestionRecord) -> None:
    result = "Correct" if question.is_correct else "Incorrect"
    if question.is_correct:
        st.success(f"{result}. You chose {question.my_answer}.")
    else:
        st.error(
            f"{result}. You chose {question.my_answer}, but the correct answer is "
            f"{question.correct_answer}."
        )

    with st.expander("Detailed Solution", expanded=True):
        st.markdown(f"**Correct Option:** {question.correct_answer}. {question.correct_option_text}")
        st.markdown(f"**Solution:** {question.solution}")
        st.markdown(f"**Shortcut:** {question.shortcut}")
        if question.formula_used:
            st.markdown("**Formula Used:** " + ", ".join(question.formula_used))
        if question.common_mistakes:
            st.markdown("**Common Mistakes:** " + ", ".join(question.common_mistakes))
        if question.tags:
            chips = "".join(
                f'<span class="topic-chip">{tag}</span>' for tag in question.tags[:8]
            )
            st.markdown(chips, unsafe_allow_html=True)


def _load_recent_questions(repository, blueprint_key: str) -> list[dict[str, Any]]:
    section = PRACTICE_BLUEPRINTS[blueprint_key]["section_name"]
    if repository.is_available():
        try:
            return repository.list_recent_questions(limit=8, section=section)
        except Exception:
            return []
    return []


def _load_attempts(repository, csv_logger, section: str) -> list[dict[str, Any]]:
    if repository.is_available():
        try:
            attempts = repository.list_recent_attempts(limit=100, section=section)
            if attempts:
                return attempts
        except Exception:
            pass
    return csv_logger.load_attempts(section=section, limit=100)
