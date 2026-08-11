import sqlite3


DB_PATH = "data/processed/financial.db"


def run_query(label, query, params):
    db = sqlite3.connect(DB_PATH)
    rows = db.execute(query, params).fetchall()
    db.close()

    print(f"\n{label}")
    print(f"Records: {len(rows)}")
    for row in rows:
        print(row)


def main():

    run_query(
        "1. Company + metric",
        """
        SELECT company, fiscal_year, quarter, metric, value
        FROM financial_facts
        WHERE company = ?
          AND metric = ?
        """,
        ("Apple", "total_revenue"),
    )

    run_query(
        "2. Add fiscal year",
        """
        SELECT company, fiscal_year, quarter, metric, value
        FROM financial_facts
        WHERE company = ?
          AND metric = ?
          AND fiscal_year = ?
        """,
        ("Apple", "total_revenue", 2003),
    )

    run_query(
        "3. Add quarter",
        """
        SELECT company, fiscal_year, quarter, metric, value
        FROM financial_facts
        WHERE company = ?
          AND metric = ?
          AND fiscal_year = ?
          AND quarter = ?
        """,
        ("Apple", "total_revenue", 2003, "2003 Q1"),
    )


if __name__ == "__main__":
    main()