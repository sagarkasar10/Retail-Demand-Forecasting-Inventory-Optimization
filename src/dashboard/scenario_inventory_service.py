from typing import Dict

import pandas as pd


def calculate_scenario_inventory_impact(
    scenario_df: pd.DataFrame,
    current_stock: float,
    lead_time_days: int,
    safety_stock_days: float,
) -> Dict[str, float]:
    """Calculate inventory impact of a demand scenario."""

    if scenario_df.empty:
        raise ValueError(
            "Scenario data cannot be empty."
        )

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

    if "scenario_demand" not in scenario_df.columns:
        raise ValueError(
            "Scenario data must contain scenario_demand."
        )

    demand = pd.to_numeric(
        scenario_df["scenario_demand"],
        errors="coerce",
    ).fillna(0).clip(lower=0)

    average_daily_demand = float(
        demand.mean()
    )

    total_scenario_demand = float(
        demand.sum()
    )

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
        0,
    )

    days_of_stock = (
        current_stock /
        average_daily_demand
        if average_daily_demand > 0
        else float("inf")
    )

    return {
        "current_stock": float(current_stock),
        "total_scenario_demand": total_scenario_demand,
        "average_daily_demand": average_daily_demand,
        "lead_time_demand": lead_time_demand,
        "safety_stock": safety_stock,
        "reorder_point": reorder_point,
        "recommended_order_quantity": (
            float(recommended_order_quantity)
        ),
        "days_of_stock": days_of_stock,
        "stockout_risk": (
            current_stock < reorder_point
        ),
    }


def create_scenario_stock_projection(
    scenario_df: pd.DataFrame,
    current_stock: float,
) -> pd.DataFrame:
    """Create projected stock levels under the scenario."""

    if scenario_df.empty:
        return pd.DataFrame()

    required_columns = {
        "forecast_date",
        "scenario_demand",
    }

    missing_columns = (
        required_columns -
        set(scenario_df.columns)
    )

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    projection_df = scenario_df[
        [
            "forecast_date",
            "scenario_demand",
        ]
    ].copy()

    projection_df["forecast_date"] = pd.to_datetime(
        projection_df["forecast_date"]
    )

    projection_df["scenario_demand"] = pd.to_numeric(
        projection_df["scenario_demand"],
        errors="coerce",
    ).fillna(0).clip(lower=0)

    projection_df = (
        projection_df
        .groupby(
            "forecast_date",
            as_index=False,
        )["scenario_demand"]
        .sum()
        .sort_values("forecast_date")
    )

    projection_df["projected_stock"] = (
        current_stock -
        projection_df["scenario_demand"].cumsum()
    )

    projection_df["stockout"] = (
        projection_df["projected_stock"] <= 0
    )

    return projection_df