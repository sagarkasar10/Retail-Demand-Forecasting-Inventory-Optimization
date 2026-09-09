from typing import Dict

import pandas as pd


def validate_price_change(
    price_change_percent: float
) -> None:
    """
    Validate price scenario input.
    """
    if price_change_percent <= -100:
        raise ValueError(
            "Price cannot be reduced by 100% or more."
        )

    if price_change_percent > 500:
        raise ValueError(
            "Price increase cannot exceed 500%."
        )


def validate_elasticity(
    elasticity: float
) -> None:
    """
    Validate price elasticity.
    """
    if elasticity > 0:
        raise ValueError(
            "For normal demand behavior, price elasticity "
            "should be zero or negative."
        )

    if elasticity < -10:
        raise ValueError(
            "Elasticity value is outside the supported range."
        )


def calculate_demand_change_percent(
    price_change_percent: float,
    elasticity: float,
) -> float:
    """
    Estimate percentage change in demand using price elasticity.
    """
    validate_price_change(price_change_percent)
    validate_elasticity(elasticity)

    return (
        elasticity *
        price_change_percent
    )


def apply_price_scenario(
    forecast_df: pd.DataFrame,
    price_change_percent: float,
    elasticity: float,
) -> pd.DataFrame:
    """
    Apply price scenario to forecast demand.
    """
    if forecast_df.empty:
        raise ValueError(
            "Forecast data cannot be empty."
        )

    if "predicted_demand" not in forecast_df.columns:
        raise ValueError(
            "Forecast data must contain predicted_demand."
        )

    demand_change_percent = (
        calculate_demand_change_percent(
            price_change_percent,
            elasticity,
        )
    )

    scenario_df = forecast_df.copy()

    scenario_df["base_demand"] = pd.to_numeric(
        scenario_df["predicted_demand"],
        errors="coerce"
    ).fillna(0)

    scenario_df["scenario_demand"] = (
        scenario_df["base_demand"] *
        (
            1 +
            demand_change_percent / 100
        )
    )

    scenario_df["scenario_demand"] = (
        scenario_df["scenario_demand"]
        .clip(lower=0)
    )

    scenario_df["demand_difference"] = (
        scenario_df["scenario_demand"] -
        scenario_df["base_demand"]
    )

    scenario_df["demand_difference_percent"] = (
        scenario_df["demand_difference"] /
        scenario_df["base_demand"].replace(0, pd.NA)
    ) * 100

    scenario_df[
        "demand_difference_percent"
    ] = scenario_df[
        "demand_difference_percent"
    ].fillna(0)

    return scenario_df


def estimate_price_elasticity_scenario(
    forecast_df: pd.DataFrame,
    price_change_percent: float,
    elasticity: float = -1.0,
) -> Dict[str, float]:
    """
    Return summarized impact of a price scenario.
    """
    scenario_df = apply_price_scenario(
        forecast_df,
        price_change_percent,
        elasticity,
    )

    base_demand = float(
        scenario_df["base_demand"].sum()
    )

    scenario_demand = float(
        scenario_df["scenario_demand"].sum()
    )

    demand_difference = (
        scenario_demand -
        base_demand
    )

    return {
        "base_demand": base_demand,
        "scenario_demand": scenario_demand,
        "demand_difference": demand_difference,
        "demand_change_percent": (
            0
            if base_demand == 0
            else (
                demand_difference /
                base_demand *
                100
            )
        ),
    }


def estimate_revenue_impact(
    scenario_df: pd.DataFrame,
    price_change_percent: float,
) -> Dict[str, float]:
    """
    Estimate revenue before and after the scenario.

    Revenue is calculated using a normalized base price of 1.
    This provides a relative revenue comparison when the
    actual price is not available in the forecast table.
    """

    if scenario_df.empty:
        return {
            "base_revenue_index": 0.0,
            "scenario_revenue_index": 0.0,
            "revenue_difference_percent": 0.0,
        }

    base_demand = float(
        scenario_df["base_demand"].sum()
    )

    scenario_demand = float(
        scenario_df["scenario_demand"].sum()
    )

    price_multiplier = (
        1 +
        price_change_percent / 100
    )

    base_revenue = base_demand

    scenario_revenue = (
        scenario_demand *
        price_multiplier
    )

    revenue_difference_percent = (
        0.0
        if base_revenue == 0
        else (
            (
                scenario_revenue -
                base_revenue
            )
            /
            base_revenue
            *
            100
        )
    )

    return {
        "base_revenue_index": base_revenue,
        "scenario_revenue_index": scenario_revenue,
        "revenue_difference_percent": (
            revenue_difference_percent
        ),
    }


def summarize_scenario(
    scenario_df: pd.DataFrame,
    price_change_percent: float = 0.0,
) -> Dict[str, float]:
    """Create scenario summary metrics."""

    base_demand = float(
        scenario_df["base_demand"].sum()
    )

    scenario_demand = float(
        scenario_df["scenario_demand"].sum()
    )

    demand_difference = (
        scenario_demand -
        base_demand
    )

    revenue = estimate_revenue_impact(
        scenario_df,
        price_change_percent,
    )

    return {
        "base_demand": base_demand,
        "scenario_demand": scenario_demand,
        "demand_difference": demand_difference,
        "demand_change_percent": (
            0.0
            if base_demand == 0
            else (
                demand_difference /
                base_demand *
                100
            )
        ),
        "base_revenue_index": revenue[
            "base_revenue_index"
        ],
        "scenario_revenue_index": revenue[
            "scenario_revenue_index"
        ],
        "revenue_difference_percent": revenue[
            "revenue_difference_percent"
        ],
    }