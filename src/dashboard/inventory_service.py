"""
Inventory analysis service for the Week 4 dashboard.

This module converts forecast demand into basic inventory
recommendations.

Important:
The M5 dataset does not provide live inventory levels.
Therefore current_stock and lead_time_days are supplied as
business inputs or simulated values by the dashboard.
"""

from __future__ import annotations

import pandas as pd


DEFAULT_LEAD_TIME_DAYS = 7
DEFAULT_SAFETY_STOCK_DAYS = 3


def validate_inventory_inputs(
    current_stock: float,
    lead_time_days: int,
    safety_stock_days: int,
) -> None:
    """
    Validate inventory-related inputs.
    """
    if current_stock < 0:
        raise ValueError(
            "Current stock cannot be negative."
        )

    if lead_time_days <= 0:
        raise ValueError(
            "Lead time must be greater than zero."
        )

    if safety_stock_days < 0:
        raise ValueError(
            "Safety stock days cannot be negative."
        )


def calculate_inventory_metrics(
    forecast_df: pd.DataFrame,
    current_stock: float,
    lead_time_days: int = DEFAULT_LEAD_TIME_DAYS,
    safety_stock_days: int = DEFAULT_SAFETY_STOCK_DAYS,
) -> dict:
    """
    Calculate inventory metrics from forecasted demand.

    Formula:

        Average Daily Demand =
            Total Forecast Demand / Forecast Days

        Lead Time Demand =
            Average Daily Demand * Lead Time

        Safety Stock =
            Average Daily Demand * Safety Stock Days

        Reorder Point =
            Lead Time Demand + Safety Stock

        Recommended Order =
            max(Reorder Point - Current Stock, 0)
    """
    validate_inventory_inputs(
        current_stock=current_stock,
        lead_time_days=lead_time_days,
        safety_stock_days=safety_stock_days,
    )

    if forecast_df.empty:
        return {
            "forecast_demand": 0.0,
            "average_daily_demand": 0.0,
            "lead_time_demand": 0.0,
            "safety_stock": 0.0,
            "reorder_point": 0.0,
            "recommended_order_quantity": 0.0,
            "stockout_risk": False,
        }

    if "predicted_demand" not in forecast_df.columns:
        raise ValueError(
            "Forecast data must contain predicted_demand."
        )

    forecast = forecast_df.copy()

    forecast["predicted_demand"] = pd.to_numeric(
        forecast["predicted_demand"],
        errors="coerce",
    )

    forecast["predicted_demand"] = (
        forecast["predicted_demand"]
        .fillna(0)
        .clip(lower=0)
    )

    forecast_demand = float(
        forecast["predicted_demand"].sum()
    )

    forecast_days = (
        forecast["forecast_date"].nunique()
        if "forecast_date" in forecast.columns
        else len(forecast)
    )

    if forecast_days <= 0:
        return {
            "forecast_demand": 0.0,
            "average_daily_demand": 0.0,
            "lead_time_demand": 0.0,
            "safety_stock": 0.0,
            "reorder_point": 0.0,
            "recommended_order_quantity": 0.0,
            "stockout_risk": False,
        }

    average_daily_demand = (
        forecast_demand / forecast_days
    )

    lead_time_demand = (
        average_daily_demand * lead_time_days
    )

    safety_stock = (
        average_daily_demand * safety_stock_days
    )

    reorder_point = (
        lead_time_demand + safety_stock
    )

    recommended_order_quantity = max(
        reorder_point - current_stock,
        0.0,
    )

    stockout_risk = (
        current_stock < lead_time_demand
    )

    return {
        "forecast_demand": forecast_demand,
        "average_daily_demand": average_daily_demand,
        "lead_time_demand": lead_time_demand,
        "safety_stock": safety_stock,
        "reorder_point": reorder_point,
        "recommended_order_quantity": recommended_order_quantity,
        "stockout_risk": stockout_risk,
    }


def calculate_inventory_by_item(
    forecast_df: pd.DataFrame,
    inventory_df: pd.DataFrame,
    lead_time_days: int = DEFAULT_LEAD_TIME_DAYS,
    safety_stock_days: int = DEFAULT_SAFETY_STOCK_DAYS,
) -> pd.DataFrame:
    """
    Calculate inventory recommendations for multiple items.

    inventory_df must contain:

        item_id
        store_id
        current_stock
    """
    required_inventory_columns = {
        "item_id",
        "store_id",
        "current_stock",
    }

    missing = (
        required_inventory_columns
        - set(inventory_df.columns)
    )

    if missing:
        raise ValueError(
            f"Missing inventory columns: {sorted(missing)}"
        )

    if forecast_df.empty:
        return pd.DataFrame()

    results = []

    grouping_columns = [
        "store_id",
        "item_id",
    ]

    for keys, group in forecast_df.groupby(
        grouping_columns
    ):
        store_id, item_id = keys

        inventory_match = inventory_df[
            (inventory_df["store_id"].astype(str) == str(store_id))
            & (inventory_df["item_id"].astype(str) == str(item_id))
        ]

        if inventory_match.empty:
            continue

        current_stock = float(
            inventory_match.iloc[0]["current_stock"]
        )

        metrics = calculate_inventory_metrics(
            forecast_df=group,
            current_stock=current_stock,
            lead_time_days=lead_time_days,
            safety_stock_days=safety_stock_days,
        )

        results.append(
            {
                "store_id": store_id,
                "item_id": item_id,
                "current_stock": current_stock,
                **metrics,
            }
        )

    return pd.DataFrame(results)