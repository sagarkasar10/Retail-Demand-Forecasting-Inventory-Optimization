"""
What-if scenario service for the Week 4 dashboard.

The preferred scenario method is to pass modified price features
through the trained LightGBM model from Week 3.

This module intentionally does not change the production forecast
table in BigQuery.
"""

from __future__ import annotations
from typing import Any
import numpy as np
import pandas as pd


MIN_PRICE = 0.0


def validate_price_change(price_change_pct: float) -> None:
    """
    Validate the requested percentage price change.

    Example:
        -10 means a 10% price decrease.
        +10 means a 10% price increase.
    """
    if price_change_pct <= -100:
        raise ValueError(
            "Price cannot be reduced by 100% or more."
        )


def apply_price_scenario(
    df: pd.DataFrame,
    price_change_pct: float,
) -> pd.DataFrame:
    """
    Apply a price-change scenario to a forecast feature DataFrame.

    The original DataFrame is not modified.
    """
    validate_price_change(price_change_pct)

    if "sell_price" not in df.columns:
        raise ValueError(
            "Scenario data must contain sell_price."
        )

    scenario_df = df.copy()

    scenario_multiplier = (
        1 + (price_change_pct / 100)
    )

    scenario_df["scenario_sell_price"] = (
        pd.to_numeric(
            scenario_df["sell_price"],
            errors="coerce",
        )
        .fillna(0)
        .clip(lower=MIN_PRICE)
        * scenario_multiplier
    )

    scenario_df["scenario_sell_price"] = (
        scenario_df["scenario_sell_price"]
        .clip(lower=MIN_PRICE)
    )

    return scenario_df


def calculate_demand_difference(
    base_demand: pd.Series | np.ndarray,
    scenario_demand: pd.Series | np.ndarray,
) -> pd.DataFrame:
    """
    Compare base and scenario predictions.
    """
    base = np.asarray(base_demand, dtype=float)
    scenario = np.asarray(scenario_demand, dtype=float)

    if len(base) != len(scenario):
        raise ValueError(
            "Base and scenario predictions must have the same length."
        )

    difference = scenario - base

    percentage_change = np.where(
        base != 0,
        (difference / base) * 100,
        np.nan,
    )

    return pd.DataFrame(
        {
            "base_demand": base,
            "scenario_demand": scenario,
            "demand_difference": difference,
            "demand_change_pct": percentage_change,
        }
    )


def run_lightgbm_scenario(
    model: Any,
    feature_df: pd.DataFrame,
    price_change_pct: float,
    feature_columns: list[str],
    price_feature_name: str = "sell_price",
) -> pd.DataFrame:
    """
    Generate scenario predictions using a trained LightGBM model.

    The model is expected to have been trained in Week 3.

    feature_df must contain:
        - the model feature columns
        - sell_price
    """
    validate_price_change(price_change_pct)

    if price_feature_name not in feature_df.columns:
        raise ValueError(
            f"Missing required price feature: {price_feature_name}"
        )

    missing_features = [
        column
        for column in feature_columns
        if column not in feature_df.columns
    ]

    if missing_features:
        raise ValueError(
            "Missing LightGBM features: "
            f"{missing_features}"
        )

    scenario_df = apply_price_scenario(
        feature_df,
        price_change_pct,
    )

    scenario_features = scenario_df[
        feature_columns
    ].copy()

    scenario_features[price_feature_name] = (
        scenario_df["scenario_sell_price"]
    )

    scenario_prediction = model.predict(
        scenario_features
    )

    scenario_prediction = np.asarray(
        scenario_prediction,
        dtype=float,
    )

    scenario_prediction = np.clip(
        scenario_prediction,
        0,
        None,
    )

    result = scenario_df.copy()

    result["base_demand"] = np.clip(
        np.asarray(
            model.predict(
                result[feature_columns]
            ),
            dtype=float,
        ),
        0,
        None,
    )

    result["scenario_demand"] = scenario_prediction

    comparison = calculate_demand_difference(
        result["base_demand"],
        result["scenario_demand"],
    )

    result[
        [
            "base_demand",
            "scenario_demand",
        ]
    ] = comparison[
        [
            "base_demand",
            "scenario_demand",
        ]
    ]

    result["demand_difference"] = (
        comparison["demand_difference"].values
    )

    result["demand_change_pct"] = (
        comparison["demand_change_pct"].values
    )

    result["price_change_pct"] = price_change_pct

    return result