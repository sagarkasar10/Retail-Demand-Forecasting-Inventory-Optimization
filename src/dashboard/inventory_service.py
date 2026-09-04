from typing import Dict

import pandas as pd


def validate_inventory_inputs(
    current_stock: float,
    lead_time_days: int,
    safety_stock_days: float,
) -> None:
    """Validate inventory planning inputs."""

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
    lead_time_days: int,
    safety_stock_days: float,
) -> Dict[str, float]:
    """
    Calculate inventory optimization metrics.
    """

    validate_inventory_inputs(
        current_stock,
        lead_time_days,
        safety_stock_days,
    )

    if forecast_df.empty:
        raise ValueError(
            "Forecast data cannot be empty."
        )

    if "predicted_demand" not in forecast_df.columns:
        raise ValueError(
            "Forecast data must contain predicted_demand."
        )

    demand = pd.to_numeric(
        forecast_df["predicted_demand"],
        errors="coerce"
    ).fillna(0)

    demand = demand.clip(lower=0)

    average_daily_demand = float(
        demand.mean()
    )

    demand_std = float(
        demand.std()
    ) if len(demand) > 1 else 0.0

    lead_time_demand = (
        average_daily_demand *
        lead_time_days
    )

    safety_stock = (
        average_daily_demand *
        safety_stock_days
    )

    reorder_point = (
        lead_time_demand +
        safety_stock
    )

    recommended_order_quantity = max(
        reorder_point - current_stock,
        0
    )

    days_of_stock = (
        current_stock / average_daily_demand
        if average_daily_demand > 0
        else float("inf")
    )

    stockout_risk = (
        current_stock < reorder_point
    )

    return {
        "average_daily_demand": average_daily_demand,
        "demand_std": demand_std,
        "lead_time_demand": lead_time_demand,
        "safety_stock": safety_stock,
        "reorder_point": reorder_point,
        "current_stock": float(current_stock),
        "recommended_order_quantity": float(
            recommended_order_quantity
        ),
        "days_of_stock": days_of_stock,
        "stockout_risk": stockout_risk,
    }


def calculate_item_inventory_status(
    forecast_df: pd.DataFrame,
    inventory_data: Dict[str, float],
) -> pd.DataFrame:
    """Calculate projected inventory for each forecast date."""

    if forecast_df.empty:
        return pd.DataFrame()

    required_columns = {
        "forecast_date",
        "predicted_demand",
    }

    missing_columns = (
        required_columns -
        set(forecast_df.columns)
    )

    if missing_columns:
        raise ValueError(
            f"Missing forecast columns: {missing_columns}"
        )

    result = forecast_df[
        [
            "forecast_date",
            "predicted_demand",
        ]
    ].copy()

    result["forecast_date"] = pd.to_datetime(
        result["forecast_date"]
    )

    result["predicted_demand"] = pd.to_numeric(
        result["predicted_demand"],
        errors="coerce"
    ).fillna(0)

    result["predicted_demand"] = (
        result["predicted_demand"]
        .clip(lower=0)
    )

    result = (
        result
        .groupby(
            "forecast_date",
            as_index=False
        )["predicted_demand"]
        .sum()
        .sort_values("forecast_date")
    )

    current_stock = float(
        inventory_data["current_stock"]
    )

    result["projected_stock"] = (
        current_stock -
        result["predicted_demand"].cumsum()
    )

    result["stockout"] = (
        result["projected_stock"] <= 0
    )

    result["stockout_date"] = result[
        "stockout"
    ].cummax()

    return result


def calculate_inventory_alert(
    inventory_metrics: Dict[str, float]
) -> str:
    """Return a simple inventory alert level."""

    if inventory_metrics["current_stock"] <= 0:
        return "CRITICAL"

    if inventory_metrics["stockout_risk"]:
        return "HIGH"

    if (
        inventory_metrics["days_of_stock"] != float("inf")
        and
        inventory_metrics["days_of_stock"] <
        inventory_metrics["lead_time_demand"]
    ):
        return "MEDIUM"

    return "LOW"


def create_inventory_summary(
    inventory_metrics: Dict[str, float]
) -> pd.DataFrame:
    """Create dashboard-friendly inventory summary."""

    alert = calculate_inventory_alert(
        inventory_metrics
    )

    return pd.DataFrame(
        {
            "Metric": [
                "Current Stock",
                "Average Daily Demand",
                "Demand Std Dev",
                "Lead Time Demand",
                "Safety Stock",
                "Reorder Point",
                "Recommended Order Quantity",
                "Days of Stock",
                "Inventory Alert",
            ],
            "Value": [
                inventory_metrics[
                    "current_stock"
                ],
                inventory_metrics[
                    "average_daily_demand"
                ],
                inventory_metrics[
                    "demand_std"
                ],
                inventory_metrics[
                    "lead_time_demand"
                ],
                inventory_metrics[
                    "safety_stock"
                ],
                inventory_metrics[
                    "reorder_point"
                ],
                inventory_metrics[
                    "recommended_order_quantity"
                ],
                inventory_metrics[
                    "days_of_stock"
                ],
                alert,
            ],
        }
    )