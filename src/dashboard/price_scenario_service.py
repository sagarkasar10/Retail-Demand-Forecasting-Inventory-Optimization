from typing import Dict

import pandas as pd


def validate_price_scenario_inputs(
    base_price: float,
    price_change_percent: float,
    elasticity: float,
) -> None:
    """Validate price scenario inputs."""

    if base_price <= 0:
        raise ValueError(
            "Base price must be greater than zero."
        )

    if price_change_percent <= -100:
        raise ValueError(
            "Price reduction cannot be 100% or more."
        )

    if price_change_percent > 500:
        raise ValueError(
            "Price increase cannot exceed 500%."
        )

    if elasticity > 0:
        raise ValueError(
            "Price elasticity must be zero or negative."
        )


def calculate_new_price(
    base_price: float,
    price_change_percent: float,
) -> float:
    """Calculate the scenario price."""

    new_price = (
        base_price *
        (1 + price_change_percent / 100)
    )

    return max(new_price, 0)


def calculate_demand_multiplier(
    price_change_percent: float,
    elasticity: float,
) -> float:
    """
    Calculate demand multiplier using price elasticity.

    Formula:
    demand change % = price change % * elasticity
    """

    demand_change_percent = (
        price_change_percent *
        elasticity
    )

    demand_multiplier = (
        1 + demand_change_percent / 100
    )

    return max(demand_multiplier, 0)


def apply_price_scenario(
    forecast_df: pd.DataFrame,
    base_price: float,
    price_change_percent: float,
    elasticity: float,
) -> pd.DataFrame:
    """Apply a price change scenario to forecast demand."""

    validate_price_scenario_inputs(
        base_price,
        price_change_percent,
        elasticity,
    )

    if forecast_df.empty:
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
            f"Missing columns: {missing_columns}"
        )

    scenario_df = forecast_df.copy()

    scenario_df["forecast_date"] = pd.to_datetime(
        scenario_df["forecast_date"]
    )

    scenario_df["base_demand"] = pd.to_numeric(
        scenario_df["predicted_demand"],
        errors="coerce",
    ).fillna(0).clip(lower=0)

    new_price = calculate_new_price(
        base_price,
        price_change_percent,
    )

    demand_multiplier = calculate_demand_multiplier(
        price_change_percent,
        elasticity,
    )

    scenario_df["base_price"] = base_price

    scenario_df["scenario_price"] = new_price

    scenario_df["scenario_demand"] = (
        scenario_df["base_demand"] *
        demand_multiplier
    )

    scenario_df["demand_difference"] = (
        scenario_df["scenario_demand"] -
        scenario_df["base_demand"]
    )

    scenario_df["base_revenue"] = (
        scenario_df["base_demand"] *
        scenario_df["base_price"]
    )

    scenario_df["scenario_revenue"] = (
        scenario_df["scenario_demand"] *
        scenario_df["scenario_price"]
    )

    scenario_df["revenue_difference"] = (
        scenario_df["scenario_revenue"] -
        scenario_df["base_revenue"]
    )

    return scenario_df


def get_price_scenario_summary(
    scenario_df: pd.DataFrame,
) -> Dict[str, float]:
    """Generate summary metrics for a price scenario."""

    if scenario_df.empty:
        return {
            "base_demand": 0.0,
            "scenario_demand": 0.0,
            "demand_change_percent": 0.0,
            "base_revenue": 0.0,
            "scenario_revenue": 0.0,
            "revenue_change_percent": 0.0,
        }

    base_demand = float(
        scenario_df["base_demand"].sum()
    )

    scenario_demand = float(
        scenario_df["scenario_demand"].sum()
    )

    base_revenue = float(
        scenario_df["base_revenue"].sum()
    )

    scenario_revenue = float(
        scenario_df["scenario_revenue"].sum()
    )

    demand_change_percent = (
        (
            (scenario_demand - base_demand)
            / base_demand
            * 100
        )
        if base_demand > 0
        else 0.0
    )

    revenue_change_percent = (
        (
            (scenario_revenue - base_revenue)
            / base_revenue
            * 100
        )
        if base_revenue > 0
        else 0.0
    )

    return {
        "base_demand": base_demand,
        "scenario_demand": scenario_demand,
        "demand_change_percent": demand_change_percent,
        "base_revenue": base_revenue,
        "scenario_revenue": scenario_revenue,
        "revenue_change_percent": revenue_change_percent,
    }
