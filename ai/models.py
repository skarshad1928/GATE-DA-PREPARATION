from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


VALID_OPTION_KEYS = ("A", "B", "C", "D")


@dataclass(slots=True)
class QuestionGenerationRequest:
    section: str
    topic: str
    difficulty: str
    session: int
    question_number: int
    exam_patterns: list[str] = field(default_factory=list)
    company_level: str = "Campus Mixed"
    recent_accuracy: float | None = None
    strong_topics: list[str] = field(default_factory=list)
    weak_topics: list[str] = field(default_factory=list)
    recent_question_summaries: list[str] = field(default_factory=list)


@dataclass(slots=True)
class PromptBundle:
    system_prompt_path: str
    generation_prompt_path: str


@dataclass(slots=True)
class QuestionRecord:
    question_id: str
    date: str
    session: int
    question_number: int
    exam_patterns: list[str]
    company_level: str
    section: str
    topic: str
    subtopic: str
    difficulty: str
    question_type: str
    question: str
    options: dict[str, str]
    correct_answer: str
    correct_option_text: str
    solution: str
    shortcut: str
    formula_used: list[str]
    common_mistakes: list[str]
    expected_time_seconds: int
    marks: int
    tags: list[str]
    my_answer: str | None = None
    time_taken_seconds: int | None = None
    is_correct: bool | None = None
    status: str = "generated"

    @classmethod
    def from_generation_payload(
        cls,
        payload: dict[str, Any],
        request: QuestionGenerationRequest,
    ) -> "QuestionRecord":
        options = payload.get("options") or {}
        cls._validate_options(options)
        correct_answer = str(payload.get("correct_answer", "")).strip().upper()
        if correct_answer not in VALID_OPTION_KEYS:
            raise ValueError("Gemini response returned an invalid correct_answer key.")

        correct_option_text = str(
            payload.get("correct_option_text") or options.get(correct_answer, "")
        ).strip()
        if not correct_option_text:
            raise ValueError("Gemini response omitted correct_option_text.")

        now = datetime.now(timezone.utc).isoformat()
        return cls(
            question_id=str(payload.get("_id") or uuid4()),
            date=str(payload.get("date") or now),
            session=request.session,
            question_number=request.question_number,
            exam_patterns=list(payload.get("exam_patterns") or request.exam_patterns),
            company_level=str(payload.get("company_level") or request.company_level),
            section=str(payload.get("section") or request.section),
            topic=str(payload.get("topic") or request.topic),
            subtopic=str(payload.get("subtopic") or request.topic),
            difficulty=str(payload.get("difficulty") or request.difficulty),
            question_type=str(payload.get("question_type") or "MCQ"),
            question=str(payload["question"]).strip(),
            options={key: str(value).strip() for key, value in options.items()},
            correct_answer=correct_answer,
            correct_option_text=correct_option_text,
            solution=str(payload["solution"]).strip(),
            shortcut=str(payload.get("shortcut") or "No shortcut available.").strip(),
            formula_used=[str(item).strip() for item in payload.get("formula_used", [])],
            common_mistakes=[
                str(item).strip() for item in payload.get("common_mistakes", [])
            ],
            expected_time_seconds=int(payload.get("expected_time_seconds", 60)),
            marks=int(payload.get("marks", 1)),
            tags=[str(item).strip() for item in payload.get("tags", [])],
            my_answer=None,
            time_taken_seconds=None,
            is_correct=None,
            status="generated",
        )

    @classmethod
    def from_document(cls, document: dict[str, Any]) -> "QuestionRecord":
        payload = dict(document)
        question_id = payload.pop("_id", payload.pop("question_id", ""))
        if not question_id:
            raise ValueError("Question document is missing an identifier.")
        return cls(question_id=question_id, **payload)

    @staticmethod
    def _validate_options(options: dict[str, Any]) -> None:
        missing = [key for key in VALID_OPTION_KEYS if key not in options]
        if missing:
            raise ValueError(f"Question options are incomplete: missing {missing}.")

    def register_attempt(self, selected_answer: str, time_taken_seconds: int) -> None:
        answer = str(selected_answer).strip().upper()
        if answer not in VALID_OPTION_KEYS:
            raise ValueError("Selected answer must be one of A, B, C, or D.")

        self.my_answer = answer
        self.time_taken_seconds = max(0, int(time_taken_seconds))
        self.is_correct = answer == self.correct_answer
        self.status = "attempted"

    def to_document(self) -> dict[str, Any]:
        return {
            "_id": self.question_id,
            "date": self.date,
            "session": self.session,
            "question_number": self.question_number,
            "exam_patterns": self.exam_patterns,
            "company_level": self.company_level,
            "section": self.section,
            "topic": self.topic,
            "subtopic": self.subtopic,
            "difficulty": self.difficulty,
            "question_type": self.question_type,
            "question": self.question,
            "options": self.options,
            "correct_answer": self.correct_answer,
            "correct_option_text": self.correct_option_text,
            "solution": self.solution,
            "shortcut": self.shortcut,
            "formula_used": self.formula_used,
            "common_mistakes": self.common_mistakes,
            "expected_time_seconds": self.expected_time_seconds,
            "marks": self.marks,
            "tags": self.tags,
            "my_answer": self.my_answer,
            "time_taken_seconds": self.time_taken_seconds,
            "is_correct": self.is_correct,
            "status": self.status,
        }

    def to_attempt_row(self) -> dict[str, Any]:
        return {
            "attempted_at": self.date,
            "question_id": self.question_id,
            "session": self.session,
            "question_number": self.question_number,
            "section": self.section,
            "topic": self.topic,
            "subtopic": self.subtopic,
            "difficulty": self.difficulty,
            "company_level": self.company_level,
            "exam_patterns": ", ".join(self.exam_patterns),
            "selected_answer": self.my_answer or "",
            "correct_answer": self.correct_answer,
            "is_correct": self.is_correct if self.is_correct is not None else "",
            "time_taken_seconds": self.time_taken_seconds or 0,
            "expected_time_seconds": self.expected_time_seconds,
            "tags": ", ".join(self.tags),
        }
