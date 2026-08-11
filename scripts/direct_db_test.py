import sqlite3


DB_PATH = "data/processed/financial.db"


def main():
    db = sqlite3.connect(DB_PATH)

    rows = db.execute(
        """
        SELECT
            company,
            fiscal_year,
            quarter,
            metric,
            value
        FROM financial_facts
        WHERE metric = 'total_revenue'
        """
    ).fetchall()

    print("=" * 80)
    print("DIRECT DATABASE TEST")
    print("=" * 80)

    print(f"Records found: {len(rows)}")

    for row in rows:
        print(row)

    db.close()


if __name__ == "__main__":
    main()