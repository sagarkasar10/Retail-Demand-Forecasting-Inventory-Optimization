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


def clean_calendar_data(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Standardize calendar data.
    """

    df = df.copy()

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    numeric_columns = [
        "wm_yr_wk",
        "wday",
        "month",
        "year",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    text_columns = [
        "weekday",
        "event_name_1",
        "event_type_1",
        "event_name_2",
        "event_type_2",
    ]

    for column in text_columns:
        if column in df.columns:
            df[column] = (
                df[column]
                .astype("string")
                .str.strip()
            )

    # Convert SNAP columns to integers
    snap_columns = [
        "snap_CA",
        "snap_TX",
        "snap_WI",
    ]

    for column in snap_columns:
        if column in df.columns:
            df[column] = (
                pd.to_numeric(
                    df[column],
                    errors="coerce"
                )
                .fillna(0)
                .astype("int64")
            )

    print(
        "✓ Calendar data standardized"
    )

    return df

