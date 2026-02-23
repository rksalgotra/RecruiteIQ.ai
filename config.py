# config.py

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME = os.getenv("APP_NAME", "TalentAIQ")
    APP_ENV = os.getenv("APP_ENV", "development")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    # HuggingFace
    HF_TOKEN = os.getenv("HF_TOKEN")
    EMBEDDING_MODEL = os.getenv(
        "EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    # Scoring Weights
    SKILL_WEIGHT = float(os.getenv("SKILL_WEIGHT", 0.35))
    EMBEDDING_WEIGHT = float(os.getenv("EMBEDDING_WEIGHT", 0.35))
    EXPERIENCE_WEIGHT = float(os.getenv("EXPERIENCE_WEIGHT", 0.30))

    # LLM
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


settings = Settings()