import sqlite3

from scripts import build_database


def test_build_database(monkeypatch, tmp_path):

    database_path = tmp_path / "test.db"
    structured_dir = tmp_path / "structured"

    structured_dir.mkdir()

    monkeypatch.setattr(
        build_database,
        "STRUCTURED_DIR",
        structured_dir,
    )

    def mock_get_connection():
        return sqlite3.connect(database_path)

    def mock_initialize_database():

        connection = sqlite3.connect(
            database_path
        )

        connection.execute(
            """
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
            """
        )

        connection.commit()
        connection.close()

    monkeypatch.setattr(
        build_database,
        "get_connection",
        mock_get_connection,
    )

    monkeypatch.setattr(
        build_database,
        "initialize_database",
        mock_initialize_database,
    )

    monkeypatch.setattr(
        build_database,
        "extract_product_revenue",
        lambda file_path: [
            {
                "quarter": "2025 Q3",
                "metric": "iphone_revenue",
                "value": 36710,
                "unit": "USD_MILLIONS",
                "source_file": "Q253.xls",
                "source_sheet": "TABLE1",
                "source_row": 20,
            }
        ],
    )

    test_excel_file = (
        structured_dir / "Q253.xls"
    )

    test_excel_file.touch()

    build_database.main()

    connection = sqlite3.connect(
        database_path
    )

    row = connection.execute(
        """
        SELECT
            company,
            fiscal_year,
            quarter,
            metric,
            category,
            value,
            unit,
            source_file,
            source_sheet,
            source_row
        FROM financial_facts
        """
    ).fetchone()

    connection.close()

    assert row is not None

    assert row[0] == "Apple"
    assert row[1] == 2025
    assert row[2] == "2025 Q3"
    assert row[3] == "iphone_revenue"
    assert row[4] == "product_revenue"
    assert row[5] == 36710
    assert row[6] == "USD_MILLIONS"
    assert row[7] == "Q253.xls"
    assert row[8] == "TABLE1"
    assert row[9] == 20