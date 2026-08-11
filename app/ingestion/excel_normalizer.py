from pathlib import Path
import pandas as pd
import re


PRODUCTS = {
    "iphone": "iphone_revenue",
    "mac": "mac_revenue",
    "ipad": "ipad_revenue",
    "wearables, home and accessories": "wearables_home_accessories_revenue",
    "services": "services_revenue",
    "total net sales": "total_revenue",
}


def clean_text(value):
    if pd.isna(value):
        return ""

    return str(value).strip()


def parse_number(value):
    """
    Convert Excel values such as:
        44582
        44,582
        -0.08
        (123)
    into numeric values.
    """

    if pd.isna(value):
        return None

    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()

    if not text:
        return None

    text = text.replace(",", "").replace("$", "")

    # Percentage values are not revenue values.
    if "%" in text:
        return None

    # Accounting negative: (123)
    if text.startswith("(") and text.endswith(")"):
        text = "-" + text[1:-1]

    try:
        return float(text)
    except ValueError:
        return None


def get_quarter_from_filename(file_path):
    """
    Convert Apple's quarterly filename into fiscal period.

    Q231 -> 2023 Q1
    Q232 -> 2023 Q2
    Q233 -> 2023 Q3

    Q241 -> 2024 Q1
    Q242 -> 2024 Q2
    Q243 -> 2024 Q3

    Q251 -> 2025 Q1
    Q252 -> 2025 Q2
    Q253 -> 2025 Q3
    """

    name = Path(file_path).stem.upper()

    match = re.fullmatch(r"Q(\d{2})(\d)", name)

    if not match:
        return None

    year_short = int(match.group(1))
    quarter = int(match.group(2))

    year = 2000 + year_short

    return f"{year} Q{quarter}"

def normalize_product_name(text):
    text = clean_text(text).lower()

    text = re.sub(r"\s+", " ", text)

    # Remove footnote markers such as (1), (2)
    text = re.sub(r"\s*\(\d+\)", "", text)

    return text.strip()


def find_product_rows(df):
    """
    Find rows containing Apple's actual product/service revenue.

    We deliberately search by row CONTENT rather than TABLE number.
    This handles differences between Q231, Q251, Q253, etc.
    """

    matches = []

    for row_index in range(len(df)):

        row = df.iloc[row_index]

        for column_index, value in enumerate(row):

            text = normalize_product_name(value)

            if not text:
                continue

            for product_name, metric_name in PRODUCTS.items():

                if text == product_name:

                    matches.append(
                        {
                            "row_index": row_index,
                            "column_index": column_index,
                            "product_name": product_name,
                            "metric": metric_name,
                        }
                    )

                    break

    return matches


def extract_values_from_row(
    df,
    row_index,
    label_column
):
    """
    Extract numeric values appearing after the product/service label.
    """

    values = []

    row = df.iloc[row_index]

    for column_index in range(label_column + 1, len(row)):

        value = parse_number(row.iloc[column_index])

        if value is not None:
            values.append(value)

    return values


def extract_product_revenue(file_path):
    """
    Extract Apple's product/service revenue only from the
    'Products and Services Performance' table.

    This avoids accidentally extracting:
        Services gross margin
        Services percentage
        Percentage of total net sales
        other unrelated tables
    """

    file_path = Path(file_path)

    records = []

    quarter = get_quarter_from_filename(file_path)

    try:
        workbook = pd.ExcelFile(
            file_path,
            engine="xlrd"
        )

    except Exception as e:
        print(
            f"Unable to open {file_path.name}: "
            f"{type(e).__name__}: {e}"
        )
        return records

    for sheet_name in workbook.sheet_names:

        try:
            df = pd.read_excel(
                workbook,
                sheet_name=sheet_name,
                header=None
            )

        except Exception:
            continue

        # ---------------------------------------------------------
        # Find the actual "Products and Services Performance" table
        # ---------------------------------------------------------

        heading_row = None

        for row_index in range(len(df)):

            row_text = " ".join(
                clean_text(value).lower()
                for value in df.iloc[row_index]
                if clean_text(value)
            )

            if "products and services performance" in row_text:

                heading_row = row_index
                break

        if heading_row is None:
            continue

        # ---------------------------------------------------------
        # Search ONLY the rows following this heading
        # ---------------------------------------------------------

        for row_index in range(
            heading_row + 1,
            min(heading_row + 30, len(df))
        ):

            row = df.iloc[row_index]

            label_column = None
            product_name = None
            metric_name = None

            # Find the product/service label
            for column_index, value in enumerate(row):

                text = normalize_product_name(value)

                if not text:
                    continue

                if text in PRODUCTS:

                    label_column = column_index
                    product_name = text
                    metric_name = PRODUCTS[text]

                    break

            if label_column is None:
                continue

            # -----------------------------------------------------
            # Extract numeric values after the label
            # -----------------------------------------------------

            values = extract_values_from_row(
                df,
                row_index,
                label_column
            )

            if not values:
                continue

            # -----------------------------------------------------
            # Revenue tables contain multiple period values.
            # First numeric value = current period.
            # -----------------------------------------------------

            value = values[0]

            records.append(
                {
                    "quarter": quarter,
                    "metric": metric_name,
                    "value": value,
                    "unit": "USD_MILLIONS",
                    "source_file": file_path.name,
                    "source_sheet": str(sheet_name),
                    "source_row": int(row_index + 1),
                }
            )

        # ---------------------------------------------------------
        # We found the real product table.
        # Don't continue searching unrelated sheets.
        # ---------------------------------------------------------

        if records:
            break

    return records

def normalize_all_files(directory):
    """
    Normalize every structured XLS file in the directory.
    """

    directory = Path(directory)

    all_records = []

    files = sorted(directory.glob("*.xls"))

    for file_path in files:

        print("=" * 80)
        print(file_path.name)
        print("=" * 80)

        records = extract_product_revenue(file_path)

        print(f"Records extracted: {len(records)}")

        all_records.extend(records)

    return all_records


if __name__ == "__main__":

    files_directory = Path(
        "data/raw/structured"
    )

    records = normalize_all_files(
        files_directory
    )

    print()
    print("=" * 80)
    print(f"TOTAL RECORDS: {len(records)}")
    print("=" * 80)

    for record in records:
        print(record)