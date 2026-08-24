import pandas as pd


def validate_sales_dataframe(
    df: pd.DataFrame
) -> bool:
    """
    Validate the cleaned sales DataFrame.
    """

    required_columns = [
        "id",
        "item_id",
        "dept_id",
        "cat_id",
        "store_id",
        "state_id"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing sales columns: {missing_columns}"
        )

    if df["id"].isna().any():
        raise ValueError(
            "Sales data contains NULL IDs."
        )

    if df["item_id"].isna().any():
        raise ValueError(
            "Sales data contains NULL item IDs."
        )

    if df["store_id"].isna().any():
        raise ValueError(
            "Sales data contains NULL store IDs."
        )

    if df["id"].duplicated().any():
        raise ValueError(
            "Sales data contains duplicate IDs."
    )

    print("✓ Sales validation passed")

    day_columns = [
        column
        for column in df.columns
        if column.startswith("d_")
    ]

    if not day_columns:
        raise ValueError(
            "Sales data contains no daily sales columns."
        )

    for column in day_columns:
        if (df[column] < 0).any():
            raise ValueError(
                f"Sales data contains negative values in {column}."
            )

    return True

def validate_calendar_dataframe(
    df: pd.DataFrame
) -> bool:
    """
    Validate the cleaned calendar DataFrame.
    """

    required_columns = [
        "date",
        "wm_yr_wk",
        "month",
        "year"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing calendar columns: {missing_columns}"
        )

    dates = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    if dates.isna().any():
        raise ValueError(
            "Calendar contains invalid dates."
        )

    invalid_months = df[
        ~df["month"].between(1, 12)
    ]

    if not invalid_months.empty:
        raise ValueError(
            "Calendar contains invalid month values."
        )
    invalid_wdays = df[
        ~df["wday"].between(1, 7)
    ]

    if not invalid_wdays.empty:
        raise ValueError(
            "Calendar contains invalid weekday values."
        )

    print("✓ Calendar validation passed")

    return True


def validate_price_dataframe(
    df: pd.DataFrame
) -> bool:
    """
    Validate the cleaned pricing DataFrame.
    """

    required_columns = [
        "store_id",
        "item_id",
        "wm_yr_wk",
        "sell_price"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing pricing columns: {missing_columns}"
        )

    prices = pd.to_numeric(
        df["sell_price"],
        errors="coerce"
    )

    if prices.isna().any():
        raise ValueError(
            "Pricing data contains invalid prices."
        )

    if (prices < 0).any():
        raise ValueError(
            "Pricing data contains negative prices."
        )

    print("✓ Pricing validation passed")

    return True


def validate_all_data(
    sales_df: pd.DataFrame,
    calendar_df: pd.DataFrame,
    prices_df: pd.DataFrame
) -> bool:
    """
    Run all DataFrame-level validation checks.
    """

    validate_sales_dataframe(
        sales_df
    )

    validate_calendar_dataframe(
        calendar_df
    )

    validate_price_dataframe(
        prices_df
    )

    print(
        "\n✓ ALL DATAFRAME VALIDATION CHECKS PASSED"
    )

    return True
