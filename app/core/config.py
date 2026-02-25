# app/core/config.py

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self):
        self.APP_NAME = os.getenv("APP_NAME", "TalentAIQ")
        self.APP_ENV = os.getenv("APP_ENV", "development")
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"

        # ==============================
        # Database
        # ==============================
        self.DATABASE_URL = "postgresql://talentaiq:password@localhost:5432/talentaiq"

        # ==============================
        # HuggingFace
        # ==============================
        self.HF_TOKEN = os.getenv("HF_TOKEN")
        self.EMBEDDING_MODEL = os.getenv(
            "EMBEDDING_MODEL",
            "sentence-transformers/all-MiniLM-L6-v2"
        )

        # ==============================
        # Scoring Weights
        # ==============================
        self.SKILL_WEIGHT = float(os.getenv("SKILL_WEIGHT", 0.35))
        self.EMBEDDING_WEIGHT = float(os.getenv("EMBEDDING_WEIGHT", 0.35))
        self.EXPERIENCE_WEIGHT = float(os.getenv("EXPERIENCE_WEIGHT", 0.30))

        # ==============================
        # Claude (Anthropic)
        # ==============================
        self.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
        self.CLAUDE_MODEL = os.getenv(
            "CLAUDE_MODEL",
            "claude-3-haiku-20240307"
        )


settings = Settings()