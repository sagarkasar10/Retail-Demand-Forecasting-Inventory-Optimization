import pandas as pd


def validate_pricing_data(
    df: pd.DataFrame
) -> dict:
    """
    Validate pricing data.
    """

    results = {}

    results["null_prices"] = int(
        df["sell_price"].isna().sum()
    )

    results["negative_prices"] = int(
        (df["sell_price"] < 0).sum()
    )

    results["zero_prices"] = int(
        (df["sell_price"] == 0).sum()
    )

    results["duplicate_keys"] = int(
        df.duplicated(
            subset=[
                "store_id",
                "item_id",
                "wm_yr_wk",
            ]
        ).sum()
    )

    print("\n========== PRICING QUALITY ==========")

    print(
        f"NULL prices      : "
        f"{results['null_prices']:,}"
    )

    print(
        f"Negative prices  : "
        f"{results['negative_prices']:,}"
    )

    print(
        f"Zero prices      : "
        f"{results['zero_prices']:,}"
    )

    print(
        f"Duplicate keys   : "
        f"{results['duplicate_keys']:,}"
    )

    print("=====================================\n")

    return results


def clean_pricing_data(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Standardize pricing data.
    Invalid prices are rejected instead of silently
    converted to NULL.
    """

    df = df.copy()

    df["store_id"] = (
        df["store_id"]
        .astype("string")
        .str.strip()
    )

    df["item_id"] = (
        df["item_id"]
        .astype("string")
        .str.strip()
    )

    df["wm_yr_wk"] = pd.to_numeric(
        df["wm_yr_wk"],
        errors="coerce"
    )

    if df["wm_yr_wk"].isna().any():
        raise ValueError(
            "Pricing data contains invalid wm_yr_wk values."
        )

    df["wm_yr_wk"] = df["wm_yr_wk"].astype("Int64")

    df["sell_price"] = pd.to_numeric(
        df["sell_price"],
        errors="coerce"
    )

    if df["sell_price"].isna().any():
        raise ValueError(
            "Pricing data contains NULL or invalid prices."
        )

    if (df["sell_price"] < 0).any():
        raise ValueError(
            "Pricing data contains negative prices."
        )

    print(
        "✓ Pricing data standardized"
    )

    return df
