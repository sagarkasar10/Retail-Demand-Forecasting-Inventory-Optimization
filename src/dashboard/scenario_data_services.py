from typing import Optional

import pandas as pd

from src.dashboard.data_access import (
    get_forecast_data,
    get_daily_sales,
)


def get_scenario_base_data(
    store_id: str,
    item_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Retrieve forecast data required for scenario analysis."""

    forecast_df = get_forecast_data(
        store_id=store_id,
        item_id=item_id,
        start_date=start_date,
        end_date=end_date,
    )

    if forecast_df.empty:
        return pd.DataFrame()

    forecast_df = forecast_df.copy()

    forecast_df["forecast_date"] = pd.to_datetime(
        forecast_df["forecast_date"]
    )

    forecast_df["predicted_demand"] = pd.to_numeric(
        forecast_df["predicted_demand"],
        errors="coerce",
    ).fillna(0)

    return (
        forecast_df
        .sort_values("forecast_date")
        .reset_index(drop=True)
    )


def get_historical_sales_for_scenario(
    store_id: str,
    item_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Retrieve historical sales data for scenario comparison."""

    sales_df = get_daily_sales(
        store_id=store_id,
        item_id=item_id,
        start_date=start_date,
        end_date=end_date,
    )

    if sales_df.empty:
        return pd.DataFrame()

    sales_df = sales_df.copy()

    sales_df["date"] = pd.to_datetime(
        sales_df["date"]
    )

    sales_df["sales"] = pd.to_numeric(
        sales_df["sales"],
        errors="coerce",
    ).fillna(0)

    if "sell_price" in sales_df.columns:
        sales_df["sell_price"] = pd.to_numeric(
            sales_df["sell_price"],
            errors="coerce",
        )

    return (
        sales_df
        .sort_values("date")
        .reset_index(drop=True)
    )


def get_latest_product_price(
    historical_sales_df: pd.DataFrame,
    default_price: float = 1.0,
) -> float:
    """Return the latest available product price."""

    if historical_sales_df.empty:
        return default_price

    if "sell_price" not in historical_sales_df.columns:
        return default_price

    price_series = (
        pd.to_numeric(
            historical_sales_df["sell_price"],
            errors="coerce",
        )
        .dropna()
    )

    if price_series.empty:
        return default_price

    latest_price = float(
        price_series.iloc[-1]
    )

    if latest_price <= 0:
        return default_price

    return latest_price