from __future__ import annotations

import json
from pathlib import Path

from ai.config import get_settings
from ai.models import PromptBundle, QuestionGenerationRequest, QuestionRecord
from utils.helpers import load_json_file, load_text_file


class GeminiConfigurationError(RuntimeError):
    """Raised when Gemini cannot be initialized in the current environment."""


class GeminiGenerationError(RuntimeError):
    """Raised when Gemini returns an invalid or unusable response."""


class GeminiQuestionService:
    def __init__(self, settings=None, client=None):
        self.settings = settings or get_settings()
        self._client = client

    def is_configured(self) -> bool:
        return bool(self.settings.gemini_api_key)

    def generate_question(
        self,
        request: QuestionGenerationRequest,
        prompt_bundle: PromptBundle,
    ) -> QuestionRecord:
        if not self.is_configured():
            raise GeminiConfigurationError(
                "Gemini is not configured. Add GEMINI_API_KEY to the environment."
            )

        system_prompt = load_text_file(Path(prompt_bundle.system_prompt_path))
        generation_template = load_text_file(Path(prompt_bundle.generation_prompt_path))
        response_schema = load_json_file(self.settings.generation_schema_path)
        contents = generation_template.format(
            section=request.section,
            topic=request.topic,
            difficulty=request.difficulty,
            session=request.session,
            question_number=request.question_number,
            exam_patterns=", ".join(request.exam_patterns)
            if request.exam_patterns
            else "GATE General Aptitude, TCS NQT, Accenture, Infosys, IBM, Amazon",
            company_level=request.company_level,
            recent_accuracy=(
                f"{request.recent_accuracy:.1f}%"
                if request.recent_accuracy is not None
                else "No previous attempts yet"
            ),
            strong_topics=", ".join(request.strong_topics)
            if request.strong_topics
            else "No strong topics detected yet",
            weak_topics=", ".join(request.weak_topics)
            if request.weak_topics
            else "No weak topics detected yet",
            recent_question_summaries=self._format_recent_questions(
                request.recent_question_summaries
            ),
        )

        if self._client is None:
            try:
                from google import genai
                from google.genai import types
            except ImportError as exc:
                raise GeminiConfigurationError(
                    "google-genai is not installed. Install dependencies from requirements.txt."
                ) from exc
            client = genai.Client(api_key=self.settings.gemini_api_key)
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=response_schema,
            )
        else:
            client = self._client
            config = {
                "system_instruction": system_prompt,
                "response_mime_type": "application/json",
                "response_schema": response_schema,
            }

        response = None
        errors: list[str] = []
        for model_name in self._candidate_models():
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=config,
                )
                break
            except Exception as exc:
                errors.append(f"{model_name}: {exc}")

        if response is None:
            joined = " | ".join(errors)
            raise GeminiGenerationError(f"Gemini request failed: {joined}")

        payload = self._extract_json_payload(response)
        return QuestionRecord.from_generation_payload(payload, request)

    def _candidate_models(self) -> list[str]:
        candidates = [
            self.settings.gemini_model,
            "gemini-3.6-flash",
            "gemini-3.5-flash-lite",
            "gemini-2.5-flash-lite",
        ]
        deduped: list[str] = []
        for model_name in candidates:
            if model_name and model_name not in deduped:
                deduped.append(model_name)
        return deduped

    @staticmethod
    def _format_recent_questions(recent_question_summaries: list[str]) -> str:
        if not recent_question_summaries:
            return "- No recent questions to avoid yet."
        return "\n".join(f"- {item}" for item in recent_question_summaries[:5])

    @staticmethod
    def _extract_json_payload(response) -> dict:
        parsed = getattr(response, "parsed", None)
        if isinstance(parsed, dict):
            return parsed

        text = getattr(response, "text", None)
        if text:
            try:
                return json.loads(text)
            except json.JSONDecodeError as exc:
                raise GeminiGenerationError(
                    "Gemini returned malformed JSON despite schema enforcement."
                ) from exc

        raise GeminiGenerationError("Gemini response did not include JSON content.")


def generate_json(prompt_file: str, user_input: str, schema_path: str) -> dict:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise GeminiConfigurationError(
            "Gemini is not configured. Add GEMINI_API_KEY to the environment."
        )

    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:
        raise GeminiConfigurationError(
            "google-genai is not installed. Install dependencies from requirements.txt."
        ) from exc

    system_prompt = load_text_file(settings.prompts_dir / prompt_file)
    schema = load_json_file(schema_path)
    client = genai.Client(api_key=settings.gemini_api_key)

    try:
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=user_input,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=schema,
            ),
        )
    except Exception as exc:
        raise GeminiGenerationError(f"Gemini request failed: {exc}") from exc

    return GeminiQuestionService._extract_json_payload(response)
