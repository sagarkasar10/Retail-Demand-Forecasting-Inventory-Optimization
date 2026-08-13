import pandas as pd


def check_sales_values(df: pd.DataFrame) -> dict:
    """
    Perform data quality checks on sales data.
    """

    results = {}

    day_columns = [
        column
        for column in df.columns
        if column.startswith("d_")
    ]

    if not day_columns:
        raise ValueError(
            "No daily sales columns found."
        )

    # Check negative sales
    negative_sales = 0

    for column in day_columns:
        negative_sales += (
            df[column] < 0
        ).sum()

    results["negative_sales"] = int(
        negative_sales
    )

    # Check missing sales
    missing_sales = 0

    for column in day_columns:
        missing_sales += (
            df[column].isna()
        ).sum()

    results["missing_sales"] = int(
        missing_sales
    )

    # Check duplicate IDs
    results["duplicate_ids"] = int(
        df["id"].duplicated().sum()
    )

    # Check missing IDs
    results["missing_ids"] = int(
        df["id"].isna().sum()
    )

    print("\n========== SALES QUALITY CHECK ==========")

    print(
        f"Daily sales columns : {len(day_columns):,}"
    )

    print(
        f"Negative sales     : "
        f"{results['negative_sales']:,}"
    )

    print(
        f"Missing sales      : "
        f"{results['missing_sales']:,}"
    )

    print(
        f"Duplicate IDs      : "
        f"{results['duplicate_ids']:,}"
    )

    print(
        f"Missing IDs        : "
        f"{results['missing_ids']:,}"
    )

    print("=========================================\n")

    return results


def clean_sales_data(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Clean sales data without changing its structure.
    """

    df = df.copy()

    day_columns = [
        column
        for column in df.columns
        if column.startswith("d_")
    ]

    for column in day_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        df[column] = (
            df[column]
            .fillna(0)
            .clip(lower=0)
        )

        df[column] = df[column].astype(
            "int64"
        )

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
