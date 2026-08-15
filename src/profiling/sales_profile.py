import pandas as pd


def profile_sales_data(
    df: pd.DataFrame
) -> dict:
    """
    Generate a data profile for the M5 sales dataset.
    """

    day_columns = [
        column
        for column in df.columns
        if column.startswith("d_")
    ]

    if not day_columns:
        raise ValueError(
            "No daily sales columns found."
        )

    total_sales = (
        df[day_columns]
        .sum()
        .sum()
    )

    average_daily_sales = (
        df[day_columns]
        .sum(axis=0)
        .mean()
    )

    maximum_daily_sales = (
        df[day_columns]
        .sum(axis=0)
        .max()
    )

    minimum_daily_sales = (
        df[day_columns]
        .sum(axis=0)
        .min()
    )

    profile = {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "daily_columns": len(day_columns),
        "unique_items": int(
            df["item_id"].nunique()
        ),
        "unique_stores": int(
            df["store_id"].nunique()
        ),
        "unique_departments": int(
            df["dept_id"].nunique()
        ),
        "unique_categories": int(
            df["cat_id"].nunique()
        ),
        "total_sales": float(
            total_sales
        ),
        "average_daily_sales": float(
            average_daily_sales
        ),
        "maximum_daily_sales": float(
            maximum_daily_sales
        ),
        "minimum_daily_sales": float(
            minimum_daily_sales
        ),
    }

    return profile


def print_sales_profile(
    profile: dict
) -> None:
    """
    Print sales profiling results.
    """

    print("\n")
    print("=" * 55)
    print("SALES DATA PROFILE")
    print("=" * 55)

    print(
        f"Rows                  : "
        f"{profile['rows']:,}"
    )

    print(
        f"Columns               : "
        f"{profile['columns']:,}"
    )

    print(
        f"Daily sales columns   : "
        f"{profile['daily_columns']:,}"
    )

    print(
        f"Unique items          : "
        f"{profile['unique_items']:,}"
    )

    print(
        f"Unique stores         : "
        f"{profile['unique_stores']:,}"
    )

    print(
        f"Unique departments    : "
        f"{profile['unique_departments']:,}"
    )

    print(
        f"Unique categories     : "
        f"{profile['unique_categories']:,}"
    )

    print(
        f"Total sales           : "
        f"{profile['total_sales']:,.0f}"
    )

    print(
        f"Average daily sales   : "
        f"{profile['average_daily_sales']:,.2f}"
    )

    print(
        f"Maximum daily sales   : "
        f"{profile['maximum_daily_sales']:,.0f}"
    )

    print(
        f"Minimum daily sales   : "
        f"{profile['minimum_daily_sales']:,.0f}"
    )

    print("=" * 55)


def get_sales_by_store(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate total sales by store.
    """

    day_columns = [
        column
        for column in df.columns
        if column.startswith("d_")
    ]

    result = (
        df.groupby("store_id")[day_columns]
        .sum()
        .sum(axis=1)
        .reset_index(name="total_sales")
    )

    return result.sort_values(
        "total_sales",
        ascending=False
    )


def get_sales_by_department(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate total sales by department.
    """

    day_columns = [
        column
        for column in df.columns
        if column.startswith("d_")
    ]

    result = (
        df.groupby("dept_id")[day_columns]
        .sum()
        .sum(axis=1)
        .reset_index(name="total_sales")
    )

    return result.sort_values(
        "total_sales",
        ascending=False
    )