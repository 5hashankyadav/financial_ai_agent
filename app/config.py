import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings:

    GROQ_API_KEY: str = os.getenv(
        "GROQ_API_KEY",
        "",
    )

    GROQ_MODEL: str = os.getenv(
        "GROQ_MODEL",
        "llama-3.3-70b-versatile",
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