import sqlite3

DB_PATH = "data/processed/financial.db"


def main():
    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()

    rows = cursor.execute("""
        SELECT
            company,
            fiscal_year,
            quarter,
            metric,
            category,
            value,
            unit,
            source_file
        FROM financial_facts
        WHERE metric = 'total_revenue'
        ORDER BY fiscal_year, quarter
    """).fetchall()

    print("=" * 100)
    print("TOTAL REVENUE RECORDS")
    print("=" * 100)

    for row in rows:
        print(row)

    db.close()


if __name__ == "__main__":
    main()