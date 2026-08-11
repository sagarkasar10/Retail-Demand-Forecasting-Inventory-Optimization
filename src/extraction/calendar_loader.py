from pathlib import Path

import pandas as pd


REQUIRED_CALENDAR_COLUMNS = [
    "date",
    "wm_yr_wk",
    "weekday",
    "wday",
    "month",
    "year",
]


def extract_calendar_data(file_path: str) -> pd.DataFrame:
    """
    Read the M5 calendar CSV file.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Calendar dataset not found: {file_path}"
        )

    if path.suffix.lower() != ".csv":
        raise ValueError(
            f"Expected CSV file, received: {path.suffix}"
        )

    print(f"Loading calendar dataset: {file_path}")

    try:
        df = pd.read_csv(path)

    except Exception as exc:
        raise RuntimeError(
            f"Failed to read calendar dataset: {exc}"
        ) from exc

    print(
        f"✓ Calendar dataset loaded successfully: "
        f"{df.shape[0]:,} rows × {df.shape[1]:,} columns"
    )

    return df


def validate_calendar_columns(df: pd.DataFrame) -> bool:
    """
    Verify mandatory calendar columns.
    """

    missing_columns = [
        column
        for column in REQUIRED_CALENDAR_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Calendar dataset is missing required columns: "
            + ", ".join(missing_columns)
        )

    print("✓ Calendar required columns are present")

    return True


def print_calendar_summary(df: pd.DataFrame) -> None:
    """
    Print basic calendar dataset information.
    """

    print("\n========== CALENDAR DATA SUMMARY ==========")
    print(f"Rows    : {df.shape[0]:,}")
    print(f"Columns : {df.shape[1]:,}")

    if "date" in df.columns:
        print(f"Min date: {df['date'].min()}")
        print(f"Max date: {df['date'].max()}")

    if "wm_yr_wk" in df.columns:
        print(
            f"Unique weeks: "
            f"{df['wm_yr_wk'].nunique():,}"
        )

    print("============================================\n")


if __name__ == "__main__":
    calendar_df = extract_calendar_data(
        "data/raw/calendar.csv"
    )

    validate_calendar_columns(calendar_df)

    print_calendar_summary(calendar_df)