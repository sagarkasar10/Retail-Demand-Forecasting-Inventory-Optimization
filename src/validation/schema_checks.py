"""
Schema validation functions for the M5 datasets.
"""

import pandas as pd


SALES_REQUIRED_COLUMNS = [
    "id",
    "item_id",
    "dept_id",
    "cat_id",
    "store_id",
    "state_id"
]


CALENDAR_REQUIRED_COLUMNS = [
    "date",
    "wm_yr_wk",
    "weekday",
    "wday",
    "month",
    "year"
]


PRICES_REQUIRED_COLUMNS = [
    "store_id",
    "item_id",
    "wm_yr_wk",
    "sell_price"
]


def check_required_columns(
    df: pd.DataFrame,
    required_columns: list[str],
    dataset_name: str
) -> dict:
    """Check whether all required columns exist."""

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        return {
            "dataset": dataset_name,
            "check": "required_columns",
            "status": "FAIL",
            "message": f"Missing columns: {missing_columns}"
        }

    return {
        "dataset": dataset_name,
        "check": "required_columns",
        "status": "PASS",
        "message": "All required columns are present."
    }


def check_dataframe_not_empty(
    df: pd.DataFrame,
    dataset_name: str
) -> dict:
    """Check whether a DataFrame is empty."""

    if df.empty:
        return {
            "dataset": dataset_name,
            "check": "not_empty",
            "status": "FAIL",
            "message": "Dataset is empty."
        }

    return {
        "dataset": dataset_name,
        "check": "not_empty",
        "status": "PASS",
        "message": f"Dataset contains {len(df):,} rows."
    }


def check_duplicate_columns(
    df: pd.DataFrame,
    dataset_name: str
) -> dict:
    """Check for duplicate column names."""

    duplicate_columns = df.columns[
        df.columns.duplicated()
    ].tolist()

    if duplicate_columns:
        return {
            "dataset": dataset_name,
            "check": "duplicate_columns",
            "status": "FAIL",
            "message": f"Duplicate columns: {duplicate_columns}"
        }

    return {
        "dataset": dataset_name,
        "check": "duplicate_columns",
        "status": "PASS",
        "message": "No duplicate column names found."
    }


def check_sales_day_columns(
    df: pd.DataFrame
) -> dict:
    """
    Check that M5 daily sales columns exist.

    M5 sales columns follow the pattern:
    d_1, d_2, d_3, ...
    """

    sales_columns = [
        column
        for column in df.columns
        if column.startswith("d_")
    ]

    if not sales_columns:
        return {
            "dataset": "sales",
            "check": "sales_day_columns",
            "status": "FAIL",
            "message": "No d_ sales columns found."
        }

    return {
        "dataset": "sales",
        "check": "sales_day_columns",
        "status": "PASS",
        "message": f"Found {len(sales_columns)} daily sales columns."
    }


def run_schema_checks(
    df: pd.DataFrame,
    required_columns: list[str],
    dataset_name: str
) -> list[dict]:
    """Run common schema checks."""

    results = [
        check_dataframe_not_empty(
            df,
            dataset_name
        ),
        check_required_columns(
            df,
            required_columns,
            dataset_name
        ),
        check_duplicate_columns(
            df,
            dataset_name
        )
    ]

    if dataset_name == "sales":
        results.append(
            check_sales_day_columns(df)
        )

    return results