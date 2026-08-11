from pathlib import Path
import pandas as pd


FILE_PATH = Path("data/raw/structured/Q251.xls")


def main():

    print("=" * 100)
    print(f"FILE: {FILE_PATH.name}")
    print("=" * 100)

    workbook = pd.ExcelFile(
        FILE_PATH,
        engine="xlrd"
    )

    for sheet_name in workbook.sheet_names:

        df = pd.read_excel(
            workbook,
            sheet_name=sheet_name,
            header=None
        )

        # Check whether this sheet contains iPhone
        contains_iphone = False

        for _, row in df.iterrows():

            row_text = " | ".join(
                str(value).strip()
                for value in row
                if pd.notna(value)
            )

            if "iphone" in row_text.lower():
                contains_iphone = True
                break

        if not contains_iphone:
            continue

        print("\n")
        print("=" * 100)
        print(f"PRODUCT TABLE FOUND: {sheet_name}")
        print(
            f"Dimensions: {df.shape[0]} rows × "
            f"{df.shape[1]} columns"
        )
        print("=" * 100)

        for index, row in df.iterrows():

            values = []

            for value in row:
                if pd.notna(value):
                    values.append(str(value).strip())

            print(
                f"Row {index}: "
                + " | ".join(values)
            )


if __name__ == "__main__":
    main()