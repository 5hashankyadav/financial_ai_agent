import sqlite3


DB_PATH = "data/processed/financial.db"


def main():
    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()

    rows = cursor.execute("""
        SELECT
            metric,
            category,
            COUNT(*) AS records
        FROM financial_facts
        GROUP BY metric, category
        ORDER BY metric, category
    """).fetchall()

    print("=" * 70)
    print("AVAILABLE FINANCIAL METRICS")
    print("=" * 70)

    for metric, category, count in rows:
        print(
            f"Metric: {metric!r} | "
            f"Category: {category!r} | "
            f"Records: {count}"
        )

    db.close()


if __name__ == "__main__":
    main()