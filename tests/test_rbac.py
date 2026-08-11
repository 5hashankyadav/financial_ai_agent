import sqlite3

from app.database.financial_queries import FinancialDatabase


def create_test_database(tmp_path):
    db_path = tmp_path / "rbac_test.db"

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
                "2025 Q1",
                "iphone_revenue",
                "product_revenue",
                69138,
                "USD_MILLIONS",
                "Q251.xls",
                "Sheet1",
                10,
            ),
            (
                "Apple",
                2025,
                "2025 Q1",
                "headcount",
                "restricted",
                164000,
                "EMPLOYEES",
                "HR.xlsx",
                "Sheet1",
                20,
            ),
        ],
    )

    connection.commit()
    connection.close()

    return db_path


def test_ceo_can_access_restricted_metric(tmp_path):
    db = FinancialDatabase(
        create_test_database(tmp_path)
    )

    results = db.get_metric(
        metric="headcount",
        fiscal_year=2025,
        quarter="Q1",
        role="CEO",
    )

    assert len(results) == 1
    assert results[0]["metric"] == "headcount"


def test_cto_cannot_access_restricted_metric(tmp_path):
    db = FinancialDatabase(
        create_test_database(tmp_path)
    )

    results = db.get_metric(
        metric="headcount",
        fiscal_year=2025,
        quarter="Q1",
        role="CTO",
    )

    assert results == []


def test_analyst_cannot_access_restricted_metric(tmp_path):
    db = FinancialDatabase(
        create_test_database(tmp_path)
    )

    results = db.get_metric(
        metric="headcount",
        fiscal_year=2025,
        quarter="Q1",
        role="ANALYST",
    )

    assert results == []


def test_restricted_roles_can_access_public_metric(tmp_path):
    db = FinancialDatabase(
        create_test_database(tmp_path)
    )

    cto_results = db.get_metric(
        metric="iphone_revenue",
        fiscal_year=2025,
        quarter="Q1",
        role="CTO",
    )

    analyst_results = db.get_metric(
        metric="iphone_revenue",
        fiscal_year=2025,
        quarter="Q1",
        role="ANALYST",
    )

    assert len(cto_results) == 1
    assert len(analyst_results) == 1


def test_period_metrics_filter_restricted_data(tmp_path):
    db = FinancialDatabase(
        create_test_database(tmp_path)
    )

    results = db.get_period_metrics(
        fiscal_year=2025,
        quarter="Q1",
        role="CTO",
    )

    metrics = {
        result["metric"]
        for result in results
    }

    assert "iphone_revenue" in metrics
    assert "headcount" not in metrics