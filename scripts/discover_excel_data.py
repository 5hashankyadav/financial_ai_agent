from pathlib import Path

import pandas as pd


STRUCTURED_DIR = Path("data/raw/structured")

KEYWORDS = [
    "net sales",
    "revenue",
    "products and services",
    "gross margin",
    "operating income",
    "net income",
    "cash and cash equivalents",
    "total assets",
    "total liabilities",
    "iphone",
    "mac",
    "ipad",
    "wearables",
    "services",
    "americas",
    "europe",
    "greater china",
    "japan",
    "asia pacific",
]


def row_contains_keyword(row):
    text = " ".join(
        str(value).strip().lower()
        for value in row
        if pd.notna(value)
    )

    return any(keyword in text for keyword in KEYWORDS)


def main():

    excel_files = sorted(
        STRUCTURED_DIR.glob("*.xls")
    )

    print("=" * 90)
    print("APPLE FINANCIAL DATA DISCOVERY")
    print("=" * 90)

    for file_path in excel_files:

        print("\n")
        print("#" * 90)
        print(f"FILE: {file_path.name}")
        print("#" * 90)

        workbook = pd.ExcelFile(
            file_path,
            engine="xlrd"
        )

        for sheet_name in workbook.sheet_names:

            df = pd.read_excel(
                workbook,
                sheet_name=sheet_name,
                header=None
            )

            matching_rows = []

            for index, row in df.iterrows():

                if row_contains_keyword(row):

                    values = [
                        str(value).strip()
                        if pd.notna(value)
                        else ""
                        for value in row
                    ]

                    matching_rows.append(
                        (index, values)
                    )

            if not matching_rows:
                continue

            print(
                f"\n[{sheet_name}] "
                f"({df.shape[0]} rows × {df.shape[1]} columns)"
            )

            for index, values in matching_rows:

                print(
                    f"Row {index:>3}: "
                    + " | ".join(values)
                )


if __name__ == "__main__":
    main()