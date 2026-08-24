import pandas as pd


def validate_calendar_dates(
    df: pd.DataFrame
) -> dict:
    """
    Validate and analyze calendar dates.
    """

    df = df.copy()

    if "date" not in df.columns:
        raise ValueError(
            "Calendar data is missing required column: date"
        )

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

    if results["null_dates"] > 0:
        raise ValueError(
            "Calendar contains NULL or invalid dates."
        )

    if results["duplicate_dates"] > 0:
        raise ValueError(
            "Calendar contains duplicate dates."
        )

    return results


def clean_calendar_data(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Standardize calendar data without silently
    hiding invalid dates or numeric values.
    """

    df = df.copy()

    if "date" not in df.columns:
        raise ValueError(
            "Calendar data is missing required column: date"
        )

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    if df["date"].isna().any():
        raise ValueError(
            "Calendar contains NULL or invalid dates."
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

            if df[column].isna().any():
                raise ValueError(
                    f"Calendar column {column} contains "
                    "invalid values."
                )

    if "month" in df.columns:

        if not df["month"].between(1, 12).all():
            raise ValueError(
                "Calendar contains invalid month values."
            )

    if "wday" in df.columns:

        if not df["wday"].between(1, 7).all():
            raise ValueError(
                "Calendar contains invalid weekday values."
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

    snap_columns = [
        "snap_CA",
        "snap_TX",
        "snap_WI",
    ]

    for column in snap_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

            if df[column].isna().any():
                raise ValueError(
                    f"Calendar column {column} contains "
                    f"invalid {column} values."
                )

            if not df[column].isin([0, 1]).all():
                raise ValueError(
                    f"Calendar column {column} must "
                    "contain only 0 or 1."
                )

            df[column] = df[column].astype("int64")

    print(
        "✓ Calendar data standardized"
    )

    return df