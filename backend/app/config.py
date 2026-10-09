import os
from pydantic_settings import BaseSettings

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "credence_ai_secret_key_demo_hackathon_2026_change_in_prod")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "credence_ai.db")
    MODEL_ARTIFACTS_DIR: str = os.getenv("MODEL_ARTIFACTS_DIR", "model_artifacts")
    SAMPLE_DATA_DIR: str = os.getenv("SAMPLE_DATA_DIR", "sample_data")
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() == "true"

settings = Settings()
