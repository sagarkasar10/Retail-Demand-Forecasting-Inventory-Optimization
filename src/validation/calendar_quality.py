import pandas as pd


def validate_calendar_dates(
    df: pd.DataFrame
) -> dict:
    """
    Validate and analyze calendar dates.
    """

    df = df.copy()

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    results = {
        "null_dates": int(
            df["date"].isna().sum()
        ),
        "duplicate_dates": int(
            df["date"].duplicated().sum()
        ),
        "minimum_date": df["date"].min(),
        "maximum_date": df["date"].max(),
    }

    print("\n========== CALENDAR QUALITY ==========")

    print(
        f"NULL dates       : "
        f"{results['null_dates']:,}"
    )

    print(
        f"Duplicate dates  : "
        f"{results['duplicate_dates']:,}"
    )

    print(
        f"Minimum date     : "
        f"{results['minimum_date']}"
    )

    print(
        f"Maximum date     : "
        f"{results['maximum_date']}"
    )

    print("======================================\n")

    return results


def clean_sales_data(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Clean sales data while preserving the M5 wide structure.
    Invalid negative sales are rejected rather than silently
    converted to zero.
    """

    df = df.copy()

    day_columns = [
        column
        for column in df.columns
        if column.startswith("d_")
    ]

    if not day_columns:
        raise ValueError(
            "No daily sales columns found."
        )

    for column in day_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        if df[column].isna().any():
            raise ValueError(
                f"Sales column {column} contains invalid "
                "or NULL values."
            )

        if (df[column] < 0).any():
            raise ValueError(
                f"Sales column {column} contains negative values."
            )

        df[column] = df[column].astype("int64")

    text_columns = [
        "id",
        "item_id",
        "dept_id",
        "cat_id",
        "store_id",
        "state_id",
    ]

    for column in text_columns:
        if column in df.columns:
            df[column] = (
                df[column]
                .astype("string")
                .str.strip()
            )

    print(
        "✓ Sales data cleaned successfully"
    )

    return df