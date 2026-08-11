import json
from pathlib import Path


INPUT_FILE = Path("data/processed/excel_inventory.json")


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        inventory = json.load(f)

    print("\n" + "=" * 80)
    print("APPLE EXCEL WORKBOOK SUMMARY")
    print("=" * 80)

    for workbook in inventory:
        print("\n" + "-" * 80)

        print(f"File   : {workbook['filename']}")
        print(f"Period : {workbook['period']}")
        print(f"Sheets : {workbook['sheet_count']}")

        print("\nSheet structure:")

        for sheet in workbook["sheets"]:
            print(
                f"  {sheet['sheet_name']:<35} "
                f"{sheet['rows']:>5} rows × "
                f"{sheet['columns']:>3} columns"
            )

    print("\n" + "=" * 80)
    print(f"Total workbooks: {len(inventory)}")
    print("=" * 80)


if __name__ == "__main__":
    main()