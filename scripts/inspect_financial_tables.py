import json
from pathlib import Path


INPUT_FILE = Path("data/processed/excel_inventory.json")

KEYWORDS = [
    "net sales",
    "revenue",
    "products",
    "services",
    "iphone",
    "mac",
    "ipad",
    "wearables",
    "gross margin",
    "operating income",
    "net income",
    "cash",
    "total assets",
    "total liabilities",
]


def contains_keyword(row):
    text = " ".join(str(value).lower() for value in row)

    return any(
        keyword in text
        for keyword in KEYWORDS
    )


def main():

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        inventory = json.load(f)

    print("\n" + "=" * 80)
    print("APPLE FINANCIAL DATA DISCOVERY")
    print("=" * 80)

    for workbook in inventory:

        print("\n" + "-" * 80)
        print(
            f"{workbook['filename']} | "
            f"{workbook['period']}"
        )
        print("-" * 80)

        for sheet in workbook["sheets"]:

            matching_rows = []

            for row in sheet["sample_rows"]:
                if contains_keyword(row):
                    matching_rows.append(row)

            if matching_rows:

                print(
                    f"\n[{sheet['sheet_name']}]"
                )

                for row in matching_rows:
                    print(
                        " | ".join(str(x) for x in row)
                    )


if __name__ == "__main__":
    main()