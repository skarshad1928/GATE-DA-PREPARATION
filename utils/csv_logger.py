from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from ai.models import QuestionRecord
from utils.helpers import ensure_parent_directory


ATTEMPT_FIELDNAMES = [
    "attempted_at",
    "question_id",
    "session",
    "question_number",
    "section",
    "topic",
    "subtopic",
    "difficulty",
    "company_level",
    "exam_patterns",
    "selected_answer",
    "correct_answer",
    "is_correct",
    "time_taken_seconds",
    "expected_time_seconds",
    "tags",
]


class CsvAttemptLogger:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        ensure_parent_directory(self.path)

    def log_attempt(self, question: QuestionRecord) -> None:
        row = question.to_attempt_row()
        file_exists = self.path.exists()
        with self.path.open("a", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=ATTEMPT_FIELDNAMES)
            if not file_exists or self.path.stat().st_size == 0:
                writer.writeheader()
            writer.writerow(row)

    def load_attempts(
        self,
        section: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []

        rows: list[dict[str, Any]] = []
        with self.path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if section and row.get("section") != section:
                    continue
                rows.append(
                    {
                        "_id": row.get("question_id", ""),
                        "date": row.get("attempted_at", ""),
                        "session": int(row.get("session") or 0),
                        "question_number": int(row.get("question_number") or 0),
                        "section": row.get("section", ""),
                        "topic": row.get("topic", ""),
                        "subtopic": row.get("subtopic", ""),
                        "difficulty": row.get("difficulty", ""),
                        "company_level": row.get("company_level", ""),
                        "exam_patterns": [
                            item.strip()
                            for item in row.get("exam_patterns", "").split(",")
                            if item.strip()
                        ],
                        "my_answer": row.get("selected_answer", ""),
                        "correct_answer": row.get("correct_answer", ""),
                        "is_correct": str(row.get("is_correct", "")).lower() == "true",
                        "time_taken_seconds": int(row.get("time_taken_seconds") or 0),
                        "expected_time_seconds": int(row.get("expected_time_seconds") or 0),
                        "tags": [
                            item.strip()
                            for item in row.get("tags", "").split(",")
                            if item.strip()
                        ],
                        "status": "attempted",
                    }
                )

        rows.sort(key=lambda item: item.get("date", ""), reverse=True)
        if limit is None:
            return rows
        return rows[:limit]
