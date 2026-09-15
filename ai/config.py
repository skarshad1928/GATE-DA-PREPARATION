from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=False)


def _as_bool(value: str | bool | None, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _first_existing_path(*paths: Path) -> Path:
    for path in paths:
        if path.exists():
            return path
    return paths[0]


def _get_secret(name: str, default: str | bool | None = None) -> str | bool | None:
    value = os.getenv(name)
    if value:
        return value
    try:
        return st.secrets.get(name, default)
    except (FileNotFoundError, KeyError, AttributeError, RuntimeError):
        return default


@dataclass(frozen=True, slots=True)
class Settings:
    base_dir: Path
    ai_dir: Path
    data_dir: Path
    database_dir: Path
    pages_dir: Path
    prompts_dir: Path
    schemas_dir: Path
    utils_dir: Path
    tests_dir: Path
    assets_dir: Path
    app_name: str
    timezone_name: str
    debug: bool
    gemini_api_key: str | None
    gemini_model: str
    mongodb_uri: str | None
    database_name: str
    question_collection: str
    session_collection: str
    user_collection: str
    logo_path: Path
    banner_path: Path
    performance_log: Path
    attempt_log: Path
    generation_schema_path: Path
    question_schema_path: Path
    prob_stats_system_prompt: Path
    prob_stats_generate_prompt: Path
    linear_algebra_system_prompt: Path
    linear_algebra_generate_prompt: Path
    calculus_optimization_system_prompt: Path
    calculus_optimization_generate_prompt: Path
    programming_dsa_system_prompt: Path
    programming_dsa_generate_prompt: Path
    dbms_system_prompt: Path
    dbms_generate_prompt: Path
    machine_learning_system_prompt: Path
    machine_learning_generate_prompt: Path
    artificial_intelligence_system_prompt: Path
    artificial_intelligence_generate_prompt: Path

    def validate_ai(self) -> list[str]:
        missing: list[str] = []
        if not self.gemini_api_key:
            missing.append("GEMINI_API_KEY")
        return missing

    def validate_database(self) -> list[str]:
        missing: list[str] = []
        if not self.mongodb_uri:
            missing.append("MONGODB_URI")
        if not self.database_name:
            missing.append("DATABASE_NAME")
        return missing


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    assets_dir = _first_existing_path(
        BASE_DIR / "assets",
        BASE_DIR / "assests",
    )

    prompts_dir = BASE_DIR / "prompts"
    schemas_dir = BASE_DIR / "schemas"
    data_dir = BASE_DIR / "data"

    return Settings(
        base_dir=BASE_DIR,
        ai_dir=BASE_DIR / "ai",
        data_dir=data_dir,
        database_dir=BASE_DIR / "database",
        pages_dir=BASE_DIR / "pages",
        prompts_dir=prompts_dir,
        schemas_dir=schemas_dir,
        utils_dir=BASE_DIR / "utils",
        tests_dir=BASE_DIR / "tests",
        assets_dir=assets_dir,
        app_name=_get_secret("APP_NAME", "GATE DA Prep Hub"),
        timezone_name=_get_secret("TIMEZONE", "Asia/Kolkata"),
        debug=_as_bool(_get_secret("DEBUG"), default=False),
        gemini_api_key=_get_secret("GEMINI_API_KEY"),
        gemini_model=_get_secret("GEMINI_MODEL", "gemini-3.6-flash"),
        mongodb_uri=_get_secret("MONGODB_URI"),
        database_name=_get_secret("DATABASE_NAME", "gate_da_prep_hub"),
        question_collection=_get_secret("QUESTION_COLLECTION", "questions"),
        session_collection=_get_secret("SESSION_COLLECTION", "sessions"),
        user_collection=_get_secret("USER_COLLECTION", "users"),
        logo_path=assets_dir / "logo.png",
        banner_path=assets_dir / "banner.png",
        performance_log=data_dir / "performance_log.csv",
        attempt_log=data_dir / "attempt_history.csv",
        generation_schema_path=schemas_dir / "generation_schema.json",
        question_schema_path=schemas_dir / "question_schema.json",
        prob_stats_system_prompt=prompts_dir / "prob_stats_system_prompt.txt",
        prob_stats_generate_prompt=prompts_dir / "prob_stats_generate_question.txt",
        linear_algebra_system_prompt=prompts_dir / "linear_algebra_system_prompt.txt",
        linear_algebra_generate_prompt=prompts_dir / "linear_algebra_generate_question.txt",
        calculus_optimization_system_prompt=prompts_dir / "calculus_optimization_system_prompt.txt",
        calculus_optimization_generate_prompt=prompts_dir / "calculus_optimization_generate_question.txt",
        programming_dsa_system_prompt=prompts_dir / "programming_dsa_system_prompt.txt",
        programming_dsa_generate_prompt=prompts_dir / "programming_dsa_generate_question.txt",
        dbms_system_prompt=prompts_dir / "dbms_system_prompt.txt",
        dbms_generate_prompt=prompts_dir / "dbms_generate_question.txt",
        machine_learning_system_prompt=prompts_dir / "machine_learning_system_prompt.txt",
        machine_learning_generate_prompt=prompts_dir / "machine_learning_generate_question.txt",
        artificial_intelligence_system_prompt=prompts_dir / "artificial_intelligence_system_prompt.txt",
        artificial_intelligence_generate_prompt=prompts_dir / "artificial_intelligence_generate_question.txt",
    )


SETTINGS = get_settings()

APP_NAME = SETTINGS.app_name
TIMEZONE = SETTINGS.timezone_name
DEBUG = SETTINGS.debug

BASE_DIR = SETTINGS.base_dir
AI_DIR = SETTINGS.ai_dir
DATA_DIR = SETTINGS.data_dir
DATABASE_DIR = SETTINGS.database_dir
PAGES_DIR = SETTINGS.pages_dir
PROMPTS_DIR = SETTINGS.prompts_dir
SCHEMAS_DIR = SETTINGS.schemas_dir
UTILS_DIR = SETTINGS.utils_dir
TESTS_DIR = SETTINGS.tests_dir
ASSETS_DIR = SETTINGS.assets_dir

GEMINI_API_KEY = SETTINGS.gemini_api_key
GEMINI_MODEL = SETTINGS.gemini_model
MONGODB_URI = SETTINGS.mongodb_uri
DATABASE_NAME = SETTINGS.database_name
QUESTION_COLLECTION = SETTINGS.question_collection
SESSION_COLLECTION = SETTINGS.session_collection
USER_COLLECTION = SETTINGS.user_collection

LOGO_PATH = SETTINGS.logo_path
BANNER_PATH = SETTINGS.banner_path
PERFORMANCE_LOG = SETTINGS.performance_log
ATTEMPT_LOG = SETTINGS.attempt_log
GENERATION_SCHEMA = SETTINGS.generation_schema_path
QUESTION_SCHEMA = SETTINGS.question_schema_path
