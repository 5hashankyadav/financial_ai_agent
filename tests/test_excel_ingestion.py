import pandas as pd
import pytest

from app.ingestion.excel_parser import (
    get_period_from_filename,
    read_excel_workbook,
)
from app.ingestion.excel_normalizer import (
    clean_text,
    parse_number,
    get_quarter_from_filename,
    normalize_product_name,
    find_product_rows,
    extract_values_from_row,
)


def test_get_period_from_filename():

    result = get_period_from_filename("Q231.xls")

    assert result["fiscal_year"] == 2023
    assert result["quarter"] == "Q1"
    assert result["period"] == "FY2023_Q1"


def test_get_period_from_filename_invalid():

    with pytest.raises(
        ValueError,
        match="Could not determine fiscal period",
    ):
        get_period_from_filename("invalid.xls")


def test_read_excel_workbook_missing_file(tmp_path):

    missing_file = tmp_path / "missing.xls"

    with pytest.raises(
        FileNotFoundError,
        match="File not found",
    ):
        read_excel_workbook(missing_file)


def test_read_excel_workbook_unsupported_format(tmp_path):

    file_path = tmp_path / "test.csv"
    file_path.write_text("test")

    with pytest.raises(
        ValueError,
        match="Unsupported Excel format",
    ):
        read_excel_workbook(file_path)


def test_clean_text():

    assert clean_text("  Apple  ") == "Apple"
    assert clean_text(None) == ""


def test_parse_number():

    assert parse_number(44582) == 44582.0
    assert parse_number("44,582") == 44582.0
    assert parse_number("$44,582") == 44582.0
    assert parse_number("(123)") == -123.0
    assert parse_number("-0.08") == -0.08

    assert parse_number("12%") is None
    assert parse_number("") is None


def test_get_quarter_from_filename():

    assert get_quarter_from_filename("Q231.xls") == "2023 Q1"
    assert get_quarter_from_filename("Q252.xls") == "2025 Q2"
    assert get_quarter_from_filename("invalid.xls") is None


def test_normalize_product_name():

    assert (
        normalize_product_name("  iPhone (1)  ")
        == "iphone"
    )

    assert (
        normalize_product_name(
            "Wearables, Home and Accessories"
        )
        == "wearables, home and accessories"
    )


def test_find_product_rows():

    dataframe = pd.DataFrame(
        [
            ["iPhone", 69138],
            ["Mac", 7999],
            ["Random text", 123],
            ["Services", 27423],
        ]
    )

    matches = find_product_rows(dataframe)

    metrics = {
        match["metric"]
        for match in matches
    }

    assert "iphone_revenue" in metrics
    assert "mac_revenue" in metrics
    assert "services_revenue" in metrics

    assert len(matches) == 3


def test_extract_values_from_row():

    dataframe = pd.DataFrame(
        [
            ["iPhone", "69,138", "66,000", "not numeric"]
        ]
    )

    values = extract_values_from_row(
        dataframe,
        row_index=0,
        label_column=0,
    )

    assert values == [
        69138.0,
        66000.0,
    ]
