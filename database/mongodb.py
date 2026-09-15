from __future__ import annotations

from typing import Any

from ai.config import get_settings
from ai.models import QuestionRecord


class DatabaseConfigurationError(RuntimeError):
    """Raised when MongoDB is not configured or dependencies are missing."""


class DatabaseOperationError(RuntimeError):
    """Raised when MongoDB operations fail."""


class MongoQuestionRepository:
    def __init__(self, settings=None, client=None):
        self.settings = settings or get_settings()
        self._client = client
        self._collection = None

    def is_configured(self) -> bool:
        return bool(self.settings.mongodb_uri and self.settings.database_name)

    def is_available(self) -> bool:
        if not self.is_configured():
            return False
        try:
            self._get_collection()
            return True
        except DatabaseConfigurationError:
            return False
        except DatabaseOperationError:
            return False

    def ensure_indexes(self) -> None:
        collection = self._get_collection()
        try:
            collection.create_index("date")
            collection.create_index("section")
            collection.create_index("topic")
            collection.create_index("status")
            collection.create_index([("section", 1), ("status", 1)])
        except Exception as exc:
            raise DatabaseOperationError(f"Failed to create MongoDB indexes: {exc}") from exc

    def save_generated_question(self, question: QuestionRecord) -> None:
        collection = self._get_collection()
        try:
            collection.replace_one(
                {"_id": question.question_id},
                question.to_document(),
                upsert=True,
            )
        except Exception as exc:
            raise DatabaseOperationError(f"Failed to save question: {exc}") from exc

    def update_attempt(self, question: QuestionRecord) -> None:
        collection = self._get_collection()
        try:
            collection.update_one(
                {"_id": question.question_id},
                {"$set": question.to_document()},
                upsert=True,
            )
        except Exception as exc:
            raise DatabaseOperationError(f"Failed to update attempt: {exc}") from exc

    def list_recent_questions(
        self,
        limit: int = 10,
        section: str | None = None,
        attempted_only: bool = False,
    ) -> list[dict[str, Any]]:
        collection = self._get_collection()
        query: dict[str, Any] = {}
        if section:
            query["section"] = section
        if attempted_only:
            query["status"] = "attempted"
        try:
            cursor = (
                collection.find(query)
                .sort("date", -1)
                .limit(max(1, int(limit)))
            )
            return list(cursor)
        except Exception as exc:
            raise DatabaseOperationError(f"Failed to fetch recent questions: {exc}") from exc

    def list_recent_attempts(
        self,
        limit: int = 50,
        section: str | None = None,
    ) -> list[dict[str, Any]]:
        return self.list_recent_questions(limit=limit, section=section, attempted_only=True)

    def _get_collection(self):
        if self._collection is not None:
            return self._collection

        if not self.is_configured():
            raise DatabaseConfigurationError(
                "MongoDB is not configured. Add MONGODB_URI and DATABASE_NAME."
            )

        try:
            from pymongo import MongoClient
        except ImportError as exc:
            raise DatabaseConfigurationError(
                "pymongo is not installed. Install dependencies from requirements.txt."
            ) from exc

        try:
            client = self._client or MongoClient(
                self.settings.mongodb_uri,
                serverSelectionTimeoutMS=4000,
            )
            database = client[self.settings.database_name]
            self._collection = database[self.settings.question_collection]
            if self._client is None:
                self._client = client
            return self._collection
        except Exception as exc:
            raise DatabaseOperationError(f"Failed to connect to MongoDB: {exc}") from exc
