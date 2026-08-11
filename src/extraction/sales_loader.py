from pathlib import Path

import pandas as pd

REQUIRED_SALES_COLUMNS = [
    "id",
    "item_id",
    "dept_id",
    "cat_id",
    "store_id",
    "state_id",
]


def extract_sales_data(file_path: str) -> pd.DataFrame:
    """
    Read the M5 sales training/validation CSV file
    and return it as a pandas DataFrame.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Sales dataset not found: {file_path}"
        )

    if path.suffix.lower() != ".csv":
        raise ValueError(
            f"Expected a CSV file, received: {path.suffix}"
        )

    print(f"Loading sales dataset: {file_path}")

    try:
        df = pd.read_csv(path)

    except Exception as exc:
        raise RuntimeError(
            f"Failed to read sales dataset: {exc}"
        ) from exc

    print(
        f"✓ Sales dataset loaded successfully: "
        f"{df.shape[0]:,} rows × {df.shape[1]:,} columns"
    )

    return df


def validate_sales_columns(df: pd.DataFrame) -> bool:
    """
    Verify that all mandatory sales columns exist.
    """

    missing_columns = [
        column
        for column in REQUIRED_SALES_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Sales dataset is missing required columns: "
            + ", ".join(missing_columns)
        )

    print("✓ Sales required columns are present")

    return True


def get_sales_summary(df: pd.DataFrame) -> dict:
    """
    Return basic information about the sales dataset.
    """

    day_columns = [
        column
        for column in df.columns
        if column.startswith("d_")
    ]

    summary = {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "day_columns": len(day_columns),
        "unique_items": df["item_id"].nunique(),
        "unique_stores": df["store_id"].nunique(),
        "unique_departments": df["dept_id"].nunique(),
        "unique_categories": df["cat_id"].nunique(),
    }

    return summary


def print_sales_summary(df: pd.DataFrame) -> None:
    """
    Print a readable sales dataset summary.
    """

    summary = get_sales_summary(df)

    print("\n========== SALES DATA SUMMARY ==========")
    print(f"Rows               : {summary['rows']:,}")
    print(f"Columns            : {summary['columns']:,}")
    print(f"Daily sales cols   : {summary['day_columns']:,}")
    print(f"Unique items       : {summary['unique_items']:,}")
    print(f"Unique stores      : {summary['unique_stores']:,}")
    print(f"Unique departments : {summary['unique_departments']:,}")
    print(f"Unique categories  : {summary['unique_categories']:,}")
    print("=========================================\n")