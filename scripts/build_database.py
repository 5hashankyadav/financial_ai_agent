from pathlib import Path

from app.database.db import (
    get_connection,
    initialize_database,
)

from app.ingestion.excel_normalizer import (
    extract_product_revenue,
)


STRUCTURED_DIR = Path(
    "data/raw/structured"
)


def main():

    print("=" * 70)
    print("BUILDING FINANCIAL DATABASE")
    print("=" * 70)

    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM financial_facts")
    connection.commit()
    connection.close()

    connection = get_connection()
    cursor = connection.cursor()

    excel_files = sorted(
        STRUCTURED_DIR.glob("*.xls")
    )

    total_records = 0

    for file_path in excel_files:

        print(
            f"\nProcessing {file_path.name}..."
        )

        records = extract_product_revenue(
            file_path
        )

        for record in records:

            cursor.execute(
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
                (
                    record.get("company", "Apple"),
                    int(record["quarter"].split()[0]),
                    record["quarter"],
                    record["metric"],
                    record.get("category", "product_revenue"),
                    record["value"],
                    record["unit"],
                    record["source_file"],
                    record["source_sheet"],
                    record["source_row"],
                )
            )

            total_records += 1

        print(
            f"  Extracted {len(records)} records"
        )

    connection.commit()
    connection.close()

    print("\n" + "=" * 70)
    print(
        f"Database created with {total_records} records."
    )
    print("=" * 70)


if __name__ == "__main__":
    main()