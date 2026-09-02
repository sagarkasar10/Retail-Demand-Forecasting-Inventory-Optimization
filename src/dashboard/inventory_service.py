"""
Inventory optimization service.

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
    Validate inventory inputs.
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
    Calculate inventory metrics from forecast demand.
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
    ).fillna(0).clip(lower=0)

    forecast_demand = float(
        forecast["predicted_demand"].sum()
    )

    if "forecast_date" in forecast.columns:
        forecast_days = (
            forecast["forecast_date"]
            .nunique()
        )
    else:
        forecast_days = len(forecast)

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
        average_daily_demand
        * lead_time_days
    )

    safety_stock = (
        average_daily_demand
        * safety_stock_days
    )

    reorder_point = (
        lead_time_demand
        + safety_stock
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
        "recommended_order_quantity": (
            recommended_order_quantity
        ),
        "stockout_risk": stockout_risk,
    }


def calculate_item_inventory_status(
    forecast_df: pd.DataFrame,
    inventory_df: pd.DataFrame,
    lead_time_days: int = DEFAULT_LEAD_TIME_DAYS,
    safety_stock_days: int = DEFAULT_SAFETY_STOCK_DAYS,
) -> pd.DataFrame:
    """
    Calculate inventory recommendations for every
    store-item combination.

    inventory_df must contain:
        store_id
        item_id
        current_stock
    """
    required_columns = {
        "store_id",
        "item_id",
        "current_stock",
    }

    missing = (
        required_columns
        - set(inventory_df.columns)
    )

    if missing:
        raise ValueError(
            "Missing inventory columns: "
            f"{sorted(missing)}"
        )

    if forecast_df.empty:
        return pd.DataFrame()

    results = []

    for (
        store_id,
        item_id,
    ), group in forecast_df.groupby(
        ["store_id", "item_id"]
    ):
        matches = inventory_df[
            (
                inventory_df["store_id"]
                .astype(str)
                == str(store_id)
            )
            & (
                inventory_df["item_id"]
                .astype(str)
                == str(item_id)
            )
        ]

        if matches.empty:
            continue

        current_stock = float(
            matches.iloc[0]["current_stock"]
        )

        metrics = calculate_inventory_metrics(
            group,
            current_stock,
            lead_time_days,
            safety_stock_days,
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


def create_inventory_summary(
    inventory_status_df: pd.DataFrame,
) -> dict:
    """
    Create high-level inventory KPIs.
    """
    if inventory_status_df.empty:
        return {
            "total_items": 0,
            "stockout_risk_items": 0,
            "total_recommended_units": 0.0,
            "average_coverage": 0.0,
        }

    stockout_risk_items = int(
        inventory_status_df[
            "stockout_risk"
        ].sum()
    )

    total_recommended_units = float(
        inventory_status_df[
            "recommended_order_quantity"
        ].sum()
    )

    coverage = (
        inventory_status_df["current_stock"]
        / inventory_status_df[
            "average_daily_demand"
        ].replace(0, pd.NA)
    )

    return {
        "total_items": len(
            inventory_status_df
        ),
        "stockout_risk_items": (
            stockout_risk_items
        ),
        "total_recommended_units": (
            total_recommended_units
        ),
        "average_coverage": float(
            coverage.dropna().mean()
        )
        if not coverage.dropna().empty
        else 0.0,
    }