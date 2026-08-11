from pathlib import Path

import pandas as pd


REQUIRED_PRICE_COLUMNS = [
    "store_id",
    "item_id",
    "wm_yr_wk",
    "sell_price",
]


def extract_prices_data(file_path: str) -> pd.DataFrame:
    """
    Read the M5 sell_prices CSV file.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Pricing dataset not found: {file_path}"
        )

    if path.suffix.lower() != ".csv":
        raise ValueError(
            f"Expected CSV file, received: {path.suffix}"
        )

    print(f"Loading pricing dataset: {file_path}")

    try:
        df = pd.read_csv(path)

    except Exception as exc:
        raise RuntimeError(
            f"Failed to read pricing dataset: {exc}"
        ) from exc

    print(
        f"✓ Pricing dataset loaded successfully: "
        f"{df.shape[0]:,} rows × {df.shape[1]:,} columns"
    )

    return df


def validate_prices_columns(df: pd.DataFrame) -> bool:
    """
    Verify mandatory pricing columns.
    """

    missing_columns = [
        column
        for column in REQUIRED_PRICE_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Pricing dataset is missing required columns: "
            + ", ".join(missing_columns)
        )

    print("✓ Pricing required columns are present")

    return True


def print_prices_summary(df: pd.DataFrame) -> None:
    """
    Print basic pricing dataset information.
    """

    print("\n========== PRICING DATA SUMMARY ==========")
    print(f"Rows    : {df.shape[0]:,}")
    print(f"Columns : {df.shape[1]:,}")

    print(
        f"Unique stores: "
        f"{df['store_id'].nunique():,}"
    )

    print(
        f"Unique items: "
        f"{df['item_id'].nunique():,}"
    )

    print(
        f"Unique weeks: "
        f"{df['wm_yr_wk'].nunique():,}"
    )

    if "sell_price" in df.columns:
        print(
            f"Minimum price: "
            f"{df['sell_price'].min()}"
        )

        print(
            f"Maximum price: "
            f"{df['sell_price'].max()}"
        )

    print("===========================================\n")

if __name__ == "__main__":

    prices_df = extract_prices_data(
        "data/raw/sell_prices.csv"
    )

    validate_prices_columns(prices_df)

    print_prices_summary(prices_df)
