from typing import Dict

import pandas as pd


def validate_promotion_inputs(
    promotion_lift_percent: float,
) -> None:
    """Validate promotion scenario input."""

    if promotion_lift_percent < -100:
        raise ValueError(
            "Promotion lift cannot be less than -100%."
        )

    if promotion_lift_percent > 1000:
        raise ValueError(
            "Promotion lift cannot exceed 1000%."
        )


def apply_promotion_scenario(
    forecast_df: pd.DataFrame,
    promotion_lift_percent: float,
) -> pd.DataFrame:
    """Apply promotional demand uplift to forecast data."""

    validate_promotion_inputs(
        promotion_lift_percent
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

    promotion_multiplier = (
        1 + promotion_lift_percent / 100
    )

    scenario_df["promotion_lift_percent"] = (
        promotion_lift_percent
    )

    scenario_df["scenario_demand"] = (
        scenario_df["base_demand"] *
        promotion_multiplier
    )

    scenario_df["scenario_demand"] = (
        scenario_df["scenario_demand"]
        .clip(lower=0)
    )

    scenario_df["additional_demand"] = (
        scenario_df["scenario_demand"] -
        scenario_df["base_demand"]
    )

    return scenario_df


def get_promotion_scenario_summary(
    scenario_df: pd.DataFrame,
) -> Dict[str, float]:
    """Create promotion scenario summary metrics."""

    if scenario_df.empty:
        return {
            "base_demand": 0.0,
            "scenario_demand": 0.0,
            "additional_demand": 0.0,
            "demand_change_percent": 0.0,
        }

    base_demand = float(
        scenario_df["base_demand"].sum()
    )

    scenario_demand = float(
        scenario_df["scenario_demand"].sum()
    )

    additional_demand = (
        scenario_demand -
        base_demand
    )

    demand_change_percent = (
        (
            additional_demand /
            base_demand *
            100
        )
        if base_demand > 0
        else 0.0
    )

    return {
        "base_demand": base_demand,
        "scenario_demand": scenario_demand,
        "additional_demand": additional_demand,
        "demand_change_percent": demand_change_percent,
    }