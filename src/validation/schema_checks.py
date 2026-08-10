"""
This module validates whether the expected columns exist
and whether basic data types are appropriate.
"""

import pandas as pd


def check_required_columns(
    df: pd.DataFrame,
    required_columns: list[str],
    dataset_name: str
) -> dict:
    """
    Check whether all required columns exist in a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Dataset to validate.

    required_columns : list[str]
        Expected columns.

    dataset_name : str
        Name of the dataset.

    Returns
    -------
    dict
        Validation result.
    """

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
    """
    Check whether a DataFrame contains at least one row.
    """

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
    """
    Check whether the DataFrame contains duplicate column names.
    """

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


def run_schema_checks(
    df: pd.DataFrame,
    required_columns: list[str],
    dataset_name: str
) -> list[dict]:
    """
    Run all basic schema checks for a dataset.
    """

    return [
        check_dataframe_not_empty(df, dataset_name),
        check_required_columns(
            df,
            required_columns,
            dataset_name
        ),
        check_duplicate_columns(df, dataset_name)
    ]