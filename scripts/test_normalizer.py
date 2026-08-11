from pathlib import Path

from app.ingestion.excel_normalizer import extract_product_revenue


def main():

    directory = Path("data/raw/structured")

    total_records = 0

    for file_path in sorted(directory.glob("*.xls")):

        print()
        print("=" * 80)
        print(file_path.name)
        print("=" * 80)

        records = extract_product_revenue(file_path)

        print(f"Records extracted: {len(records)}")

        for record in records:
            print(record)

        total_records += len(records)

    print()
    print("=" * 80)
    print(f"TOTAL RECORDS: {total_records}")
    print("=" * 80)


if __name__ == "__main__":
    main()