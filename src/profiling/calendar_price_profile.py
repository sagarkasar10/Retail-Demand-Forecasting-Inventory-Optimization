import pandas as pd


def profile_calendar_data(
    df: pd.DataFrame
) -> dict:
    """
    Generate a profile of calendar data.
    """

    date_series = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    profile = {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "unique_dates": int(
            date_series.nunique()
        ),
        "null_dates": int(
            date_series.isna().sum()
        ),
        "minimum_date": date_series.min(),
        "maximum_date": date_series.max(),
        "unique_week_numbers": int(
            df["wm_yr_wk"].nunique()
        ),
    }

    return profile


def print_calendar_profile(
    profile: dict
) -> None:
    """
    Print calendar profiling results.
    """

    print("\n")
    print("=" * 55)
    print("CALENDAR DATA PROFILE")
    print("=" * 55)

    print(
        f"Rows              : "
        f"{profile['rows']:,}"
    )

    print(
        f"Columns           : "
        f"{profile['columns']:,}"
    )

    print(
        f"Unique dates      : "
        f"{profile['unique_dates']:,}"
    )

    print(
        f"NULL dates        : "
        f"{profile['null_dates']:,}"
    )

    print(
        f"Minimum date      : "
        f"{profile['minimum_date']}"
    )

    print(
        f"Maximum date      : "
        f"{profile['maximum_date']}"
    )

    print(
        f"Unique weeks      : "
        f"{profile['unique_week_numbers']:,}"
    )

    print("=" * 55)


def profile_price_data(
    df: pd.DataFrame
) -> dict:
    """
    Generate a profile of pricing data.
    """

    prices = pd.to_numeric(
        df["sell_price"],
        errors="coerce"
    )

    profile = {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "unique_items": int(
            df["item_id"].nunique()
        ),
        "unique_stores": int(
            df["store_id"].nunique()
        ),
        "unique_weeks": int(
            df["wm_yr_wk"].nunique()
        ),
        "null_prices": int(
            prices.isna().sum()
        ),
        "minimum_price": float(
            prices.min()
        ),
        "maximum_price": float(
            prices.max()
        ),
        "average_price": float(
            prices.mean()
        ),
    }

    return profile


def print_price_profile(
    profile: dict
) -> None:
    """
    Print pricing profiling results.
    """

    print("\n")
    print("=" * 55)
    print("PRICING DATA PROFILE")
    print("=" * 55)

    print(
        f"Rows              : "
        f"{profile['rows']:,}"
    )

    print(
        f"Columns           : "
        f"{profile['columns']:,}"
    )

    print(
        f"Unique items      : "
        f"{profile['unique_items']:,}"
    )

    print(
        f"Unique stores     : "
        f"{profile['unique_stores']:,}"
    )

    print(
        f"Unique weeks      : "
        f"{profile['unique_weeks']:,}"
    )

    print(
        f"NULL prices       : "
        f"{profile['null_prices']:,}"
    )

    print(
        f"Minimum price     : "
        f"{profile['minimum_price']:.2f}"
    )

    print(
        f"Maximum price     : "
        f"{profile['maximum_price']:.2f}"
    )

    print(
        f"Average price     : "
        f"{profile['average_price']:.2f}"
    )

    print("=" * 55)