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


def prepare_forecast_demand(
    forecast_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare and validate final forecast data for
    inventory calculations.

    Forecast demand is aggregated by forecast date so that
    inventory calculations always use the final daily forecast.
    """

    if forecast_df is None or forecast_df.empty:
        raise ValueError(
            "Forecast data cannot be empty."
        )

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
            "Forecast data is missing required columns: "
            f"{sorted(missing_columns)}"
        )

    result = forecast_df[
        [
            "forecast_date",
            "predicted_demand",
        ]
    ].copy()

    result["forecast_date"] = pd.to_datetime(
        result["forecast_date"],
        errors="coerce",
    )

    if result["forecast_date"].isna().any():
        raise ValueError(
            "Forecast data contains invalid forecast dates."
        )

    result["predicted_demand"] = pd.to_numeric(
        result["predicted_demand"],
        errors="coerce",
    ).fillna(0)

    result["predicted_demand"] = (
        result["predicted_demand"]
        .clip(lower=0)
    )

    result = (
        result
        .groupby(
            "forecast_date",
            as_index=False,
        )["predicted_demand"]
        .sum()
        .sort_values("forecast_date")
        .reset_index(drop=True)
    )

    if result.empty:
        raise ValueError(
            "No valid forecast demand is available."
        )

    return result


def calculate_inventory_metrics(
    forecast_df: pd.DataFrame,
    current_stock: float,
    lead_time_days: int,
    safety_stock_days: float,
) -> Dict[str, float]:
    """
    Calculate inventory metrics using the final forecast data.

    Calculations:
        Average Daily Demand =
            Mean predicted demand from the final forecast.

        Lead Time Demand =
            Average Daily Demand × Lead Time Days

        Safety Stock =
            Average Daily Demand × Safety Stock Days

        Reorder Point =
            Lead Time Demand + Safety Stock

        Recommended Order Quantity =
            max(Reorder Point - Current Stock, 0)

        Days of Stock =
            Current Stock / Average Daily Demand

        Stockout Risk =
            Current Stock <= Reorder Point
    """

    validate_inventory_inputs(
        current_stock=current_stock,
        lead_time_days=lead_time_days,
        safety_stock_days=safety_stock_days,
    )

    demand_df = prepare_forecast_demand(
        forecast_df
    )

    demand = demand_df["predicted_demand"]

    average_daily_demand = float(
        demand.mean()
    )

    demand_std = float(
        demand.std(ddof=0)
    ) if len(demand) > 1 else 0.0

    forecast_horizon_days = int(
        len(demand_df)
    )

    total_forecast_demand = float(
        demand.sum()
    )

    lead_time_demand = float(
        average_daily_demand *
        lead_time_days
    )

    safety_stock = float(
        average_daily_demand *
        safety_stock_days
    )

    reorder_point = float(
        lead_time_demand +
        safety_stock
    )

    recommended_order_quantity = float(
        max(
            reorder_point - current_stock,
            0,
        )
    )

    if average_daily_demand > 0:
        days_of_stock = float(
            current_stock /
            average_daily_demand
        )
    else:
        days_of_stock = float("inf")

    stockout_risk = bool(
        current_stock <= reorder_point
    )

    return {
        "current_stock": float(current_stock),
        "average_daily_demand": average_daily_demand,
        "demand_std": demand_std,
        "forecast_horizon_days": forecast_horizon_days,
        "total_forecast_demand": total_forecast_demand,
        "lead_time_demand": lead_time_demand,
        "safety_stock": safety_stock,
        "reorder_point": reorder_point,
        "recommended_order_quantity": (
            recommended_order_quantity
        ),
        "days_of_stock": days_of_stock,
        "stockout_risk": stockout_risk,
    }


def calculate_item_inventory_status(
    forecast_df: pd.DataFrame,
    inventory_data: Dict[str, float],
) -> pd.DataFrame:
    """
    Calculate projected inventory using final forecast demand.

    The projected stock is reduced day by day using the
    final predicted demand.
    """

    demand_df = prepare_forecast_demand(
        forecast_df
    )

    if "current_stock" not in inventory_data:
        raise ValueError(
            "Inventory data must contain current_stock."
        )

    current_stock = float(
        inventory_data["current_stock"]
    )

    if current_stock < 0:
        raise ValueError(
            "Current stock cannot be negative."
        )

    result = demand_df.copy()

    result["cumulative_forecast_demand"] = (
        result["predicted_demand"].cumsum()
    )

    result["projected_stock"] = (
        current_stock -
        result["cumulative_forecast_demand"]
    )

    result["stockout"] = (
        result["projected_stock"] <= 0
    )

    stockout_dates = result.loc[
        result["stockout"],
        "forecast_date",
    ]

    if stockout_dates.empty:
        first_stockout_date = pd.NaT
    else:
        first_stockout_date = (
            stockout_dates.iloc[0]
        )

    result["stockout_date"] = (
        first_stockout_date
    )

    return result


def calculate_inventory_alert(
    inventory_metrics: Dict[str, float],
) -> str:
    """
    Return inventory alert level.

    CRITICAL:
        Stock is already zero.

    HIGH:
        Current stock is at or below reorder point.

    MEDIUM:
        Stock is above reorder point but available
        coverage is less than lead time + safety stock.

    LOW:
        Inventory coverage is sufficient.
    """

    current_stock = (
        inventory_metrics["current_stock"]
    )

    if current_stock <= 0:
        return "CRITICAL"

    if inventory_metrics["stockout_risk"]:
        return "HIGH"

    days_of_stock = (
        inventory_metrics["days_of_stock"]
    )

    lead_time_days = (
        inventory_metrics["lead_time_demand"] /
        inventory_metrics["average_daily_demand"]
        if inventory_metrics["average_daily_demand"] > 0
        else 0
    )

    safety_stock_days = (
        inventory_metrics["safety_stock"] /
        inventory_metrics["average_daily_demand"]
        if inventory_metrics["average_daily_demand"] > 0
        else 0
    )

    minimum_coverage_days = (
        lead_time_days +
        safety_stock_days
    )

    if (
        days_of_stock != float("inf")
        and days_of_stock < minimum_coverage_days
    ):
        return "MEDIUM"

    return "LOW"


def create_inventory_summary(
    inventory_metrics: Dict[str, float],
) -> pd.DataFrame:
    """Create a dashboard-friendly inventory summary."""

    alert = calculate_inventory_alert(
        inventory_metrics
    )

    days_of_stock = (
        inventory_metrics["days_of_stock"]
    )

    display_days_of_stock = (
        "Unlimited"
        if days_of_stock == float("inf")
        else round(days_of_stock, 2)
    )

    return pd.DataFrame(
        {
            "Metric": [
                "Current Stock",
                "Average Daily Demand",
                "Demand Std Dev",
                "Forecast Horizon (Days)",
                "Total Forecast Demand",
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
                    "forecast_horizon_days"
                ],
                inventory_metrics[
                    "total_forecast_demand"
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
                display_days_of_stock,
                alert,
            ],
        }
    )