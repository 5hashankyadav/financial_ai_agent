from pathlib import Path
import re

import pandas as pd


def get_period_from_filename(filename: str) -> dict:
    """
    Convert Apple's quarterly filename into fiscal year/quarter metadata.

    Examples:
        Q231.xls -> FY2023 Q1
        Q232.xls -> FY2023 Q2
        Q233.xls -> FY2023 Q3
        Q241.xls -> FY2024 Q1
    """

    name = Path(filename).stem.upper()

    match = re.fullmatch(r"Q(\d{2})(\d)", name)

    if not match:
        raise ValueError(
            f"Could not determine fiscal period from filename: {filename}"
        )

    year_short = int(match.group(1))
    quarter = int(match.group(2))

    fiscal_year = 2000 + year_short

    return {
        "fiscal_year": fiscal_year,
        "quarter": f"Q{quarter}",
        "period": f"FY{fiscal_year}_Q{quarter}",
    }


def read_excel_workbook(file_path: str) -> dict[str, pd.DataFrame]:
    """
    Read all sheets from an XLS/XLSX workbook.

    Returns:
        Dictionary:
            {
                "SHEET_NAME": DataFrame,
                ...
            }
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    extension = path.suffix.lower()

    if extension == ".xls":
        engine = "xlrd"
    elif extension == ".xlsx":
        engine = "openpyxl"
    else:
        raise ValueError(
            f"Unsupported Excel format: {extension}"
        )

    workbook = pd.ExcelFile(path, engine=engine)

    sheets = {}

    for sheet_name in workbook.sheet_names:

        df = pd.read_excel(
            workbook,
            sheet_name=sheet_name,
            header=None
        )

        sheets[sheet_name] = df

    return sheets


def inspect_workbook(file_path: str) -> dict:
    """
    Inspect an Apple financial workbook without modifying it.

    Returns metadata about:
        - filename
        - fiscal period
        - sheets
        - dimensions
        - sample rows
    """

    path = Path(file_path)

    period_info = get_period_from_filename(path.name)

    sheets = read_excel_workbook(path)

    sheet_info = []

    for sheet_name, df in sheets.items():

        sample = df.head(10).fillna("").astype(str).values.tolist()

        sheet_info.append(
            {
                "sheet_name": sheet_name,
                "rows": int(df.shape[0]),
                "columns": int(df.shape[1]),
                "sample_rows": sample,
            }
        )

    return {
        "filename": path.name,
        "file_path": str(path),
        **period_info,
        "sheet_count": len(sheets),
        "sheets": sheet_info,
    }