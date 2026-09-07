"""
Tests for the Week 4 scenario service.
"""

import pandas as pd
import pytest

from src.dashboard.scenario_service import (
    apply_price_scenario,
    calculate_demand_difference,
)


def test_price_decrease():
    """
    Verify a 10% price reduction.
    """
    df = pd.DataFrame(
        {
            "sell_price": [100.0, 200.0],
        }
    )

    result = apply_price_scenario(
        df,
        -10,
    )

    assert result["scenario_sell_price"].tolist() == [
        90.0,
        180.0,
    ]


def test_price_increase():
    """
    Verify a 10% price increase.
    """
    df = pd.DataFrame(
        {
            "sell_price": [100.0],
        }
    )

    result = apply_price_scenario(
        df,
        10,
    )

    assert result["scenario_sell_price"].iloc[0] == 110.0


def test_invalid_price_change():
    """
    Verify that a 100% or greater price reduction is rejected.
    """
    df = pd.DataFrame(
        {
            "sell_price": [100.0],
        }
    )

    with pytest.raises(ValueError):
        apply_price_scenario(
            df,
            -100,
        )


def test_demand_difference():
    """
    Verify base-vs-scenario demand calculations.
    """
    result = calculate_demand_difference(
        base_demand=[100, 200],
        scenario_demand=[110, 180],
    )

    assert result["demand_difference"].tolist() == [
        10.0,
        -20.0,
    ]

    assert result["demand_change_pct"].tolist() == [
        10.0,
        -10.0,
    ]