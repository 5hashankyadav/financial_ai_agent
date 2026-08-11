import sqlite3
from app.config import settings


DATABASE_PATH = settings.DATABASE_PATH


def get_connection():
    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(DATABASE_PATH)

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS financial_facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            company TEXT NOT NULL,

            fiscal_year INTEGER NOT NULL,
            quarter TEXT,

            metric TEXT NOT NULL,
            category TEXT,

            value REAL,
            unit TEXT,

            source_file TEXT NOT NULL,
            source_sheet TEXT,
            source_row INTEGER,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_financial_period
        ON financial_facts (
            fiscal_year,
            quarter
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_financial_metric
        ON financial_facts (
            metric
        )
    """)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    initialize_database()
    print("Database initialized.")