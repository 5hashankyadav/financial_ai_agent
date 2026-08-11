import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings:

    GEMINI_API_KEY: str = os.getenv(
        "GEMINI_API_KEY",
        "",
    )

    GEMINI_MODEL: str = os.getenv(
        "GEMINI_MODEL",
        "gemini-3.6-flash",
    )

    DATABASE_PATH: Path = BASE_DIR / os.getenv(
        "DATABASE_PATH",
        "data/processed/financial.db",
    )

    FAISS_INDEX_PATH: Path = BASE_DIR / os.getenv(
        "FAISS_INDEX_PATH",
        "data/processed/faiss.index",
    )

    CHUNKS_PATH: Path = BASE_DIR / os.getenv(
        "CHUNKS_PATH",
        "data/processed/chunks.pkl",
    )


settings = Settings()