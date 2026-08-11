import json
from pathlib import Path

from app.ingestion.excel_parser import inspect_workbook


STRUCTURED_DIR = Path("data/raw/structured")
OUTPUT_DIR = Path("data/processed")
OUTPUT_FILE = OUTPUT_DIR / "excel_inventory.json"


def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    excel_files = sorted(
        list(STRUCTURED_DIR.glob("*.xls"))
        + list(STRUCTURED_DIR.glob("*.xlsx"))
    )

    if not excel_files:
        print("No Excel files found.")
        return

    print(f"Found {len(excel_files)} Excel files.\n")

    inventory = []

    for file_path in excel_files:

        print("=" * 70)
        print(f"Processing: {file_path.name}")

        try:

            info = inspect_workbook(file_path)

            inventory.append(info)

            print(
                f"Period: {info['period']}"
            )

            print(
                f"Sheets: {info['sheet_count']}"
            )

            for sheet in info["sheets"]:

                print(
                    f"  - {sheet['sheet_name']}: "
                    f"{sheet['rows']} rows × "
                    f"{sheet['columns']} columns"
                )

        except Exception as e:

            print(
                f"ERROR: {file_path.name}: {e}"
            )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            inventory,
            f,
            indent=2,
            ensure_ascii=False
        )

    print("\n" + "=" * 70)
    print("Excel inspection complete.")
    print(f"Inventory saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()