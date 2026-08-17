import pandas as pd


def create_sales_summary(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Create a summary of sales by store and department.
    """

    day_columns = [
        column
        for column in df.columns
        if column.startswith("d_")
    ]

    if not day_columns:
        raise ValueError(
            "No daily sales columns were found."
        )

    temp_df = df.copy()

    temp_df["total_sales"] = (
        temp_df[day_columns]
        .sum(axis=1)
    )

    summary = (
        temp_df
        .groupby(
            ["store_id", "dept_id"],
            as_index=False
        )["total_sales"]
        .sum()
    )

    return summary.sort_values(
        "total_sales",
        ascending=False
    )


def create_item_summary(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Create item-level sales summary.
    """

    day_columns = [
        column
        for column in df.columns
        if column.startswith("d_")
    ]

    temp_df = df.copy()

    temp_df["total_sales"] = (
        temp_df[day_columns]
        .sum(axis=1)
    )

    summary = (
        temp_df[
            [
                "item_id",
                "store_id",
                "dept_id",
                "cat_id",
                "total_sales"
            ]
        ]
        .sort_values(
            "total_sales",
            ascending=False
        )
    )

    return summary


def create_calendar_summary(
    df: pd.DataFrame
) -> dict:
    """
    Create summary information for calendar data.
    """

    dates = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    return {
        "row_count": len(df),
        "unique_dates": int(
            dates.nunique()
        ),
        "minimum_date": dates.min(),
        "maximum_date": dates.max(),
        "event_days": int(
            df["event_name_1"].notna().sum()
        ),
        "snap_ca_days": int(
            df["snap_CA"].sum()
        ),
        "snap_tx_days": int(
            df["snap_TX"].sum()
        ),
        "snap_wi_days": int(
            df["snap_WI"].sum()
        )
    }


def create_price_summary(
    df: pd.DataFrame
) -> dict:
    """
    Create summary information for pricing data.
    """

    prices = pd.to_numeric(
        df["sell_price"],
        errors="coerce"
    )

    return {
        "row_count": len(df),
        "unique_items": int(
            df["item_id"].nunique()
        ),
        "unique_stores": int(
            df["store_id"].nunique()
        ),
        "unique_weeks": int(
            df["wm_yr_wk"].nunique()
        ),
        "minimum_price": float(
            prices.min()
        ),
        "maximum_price": float(
            prices.max()
        ),
        "average_price": float(
            prices.mean()
        )
    }


def print_pipeline_summary(
    sales_df: pd.DataFrame,
    calendar_df: pd.DataFrame,
    prices_df: pd.DataFrame
) -> None:
    """
    Print final Week 1 data summary.
    """

    print("\n")
    print("=" * 70)
    print("WEEK 1 DATA SUMMARY")
    print("=" * 70)

    print("\nSALES")
    print("-" * 40)

    print(
        f"Rows: {len(sales_df):,}"
    )

    print(
        f"Items: {sales_df['item_id'].nunique():,}"
    )

    print(
        f"Stores: {sales_df['store_id'].nunique():,}"
    )

    print("\nCALENDAR")
    print("-" * 40)

    calendar_summary = create_calendar_summary(
        calendar_df
    )

    for key, value in calendar_summary.items():
        print(
            f"{key}: {value}"
        )

    print("\nPRICES")
    print("-" * 40)

    price_summary = create_price_summary(
        prices_df
    )

    for key, value in price_summary.items():
        print(
            f"{key}: {value}"
        )

    print("\n" + "=" * 70)