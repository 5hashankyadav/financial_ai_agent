from app.database.db import get_connection


def main():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            fiscal_year,
            quarter,
            metric,
            category,
            value,
            source_file
        FROM financial_facts
        ORDER BY
            fiscal_year,
            quarter,
            id
    """)

    rows = cursor.fetchall()

    print("\n" + "=" * 90)
    print("FINANCIAL DATABASE")
    print("=" * 90)

    for row in rows:
        print(
            f"{row['fiscal_year']} "
            f"{row['quarter']} | "
            f"{row['metric']:<40} | "
            f"{row['value']:>10} | "
            f"{row['source_file']}"
        )

    print("\n" + "=" * 90)
    print(f"Total records: {len(rows)}")
    print("=" * 90)

    print("\n" + "=" * 90)
    print("RECORDS BY SOURCE FILE")
    print("=" * 90)

    cursor.execute("""
        SELECT
            source_file,
            COUNT(*) AS record_count
        FROM financial_facts
        GROUP BY source_file
        ORDER BY source_file
    """)

    source_rows = cursor.fetchall()

    for row in source_rows:
        print(
            f"{row['source_file']:<15} "
            f"{row['record_count']} records"
        )

    connection.close()


if __name__ == "__main__":
    main()