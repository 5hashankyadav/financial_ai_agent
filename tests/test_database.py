import sqlite3

from app.database.financial_queries import FinancialDatabase


def create_test_database(db_path):
    connection = sqlite3.connect(db_path)

    connection.execute("""
        CREATE TABLE financial_facts (
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
            source_row INTEGER
        )
    """)

    connection.executemany(
        """
        INSERT INTO financial_facts (
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
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                "Apple",
                2025,
                "2025 Q3",
                "net_sales",
                None,
                94036,
                "USD_MILLIONS",
                "FY25_Q3.pdf",
                None,
                None,
            ),
            (
                "Apple",
                2025,
                "2025 Q3",
                "revenue",
                "iPhone",
                36710,
                "USD_MILLIONS",
                "FY25_Q3.pdf",
                None,
                None,
            ),
            (
                "Apple",
                2025,
                "2022 Q1",
                "net_sales",
                None,
                117154,
                "USD_MILLIONS",
                "Q1_FY23.xls",
                "TABLE21",
                24,
            ),
        ],
    )

    connection.commit()
    connection.close()


def test_get_metric(tmp_path):

    db_path = tmp_path / "test.db"

    create_test_database(db_path)

    database = FinancialDatabase(db_path)

    result = database.get_metric(
        metric="net_sales",
        fiscal_year=2025,
        quarter="Q3",
    )

    assert len(result) == 1
    assert result[0]["value"] == 94036
    assert result[0]["unit"] == "USD_MILLIONS"
    assert result[0]["source_file"] == "FY25_Q3.pdf"


def test_get_metric_with_category(tmp_path):

    db_path = tmp_path / "test.db"

    create_test_database(db_path)

    database = FinancialDatabase(db_path)

    result = database.get_metric(
        metric="revenue",
        fiscal_year=2025,
        quarter="Q3",
        category="iPhone",
    )

    assert len(result) == 1
    assert result[0]["value"] == 36710
    assert result[0]["category"] == "iPhone"


def test_get_period_metrics(tmp_path):

    db_path = tmp_path / "test.db"

    create_test_database(db_path)

    database = FinancialDatabase(db_path)

    result = database.get_period_metrics(
        fiscal_year=2025,
        quarter="Q3",
    )

    assert len(result) == 2

    metrics = {
        row["metric"]
        for row in result
    }

    assert "net_sales" in metrics
    assert "revenue" in metrics
