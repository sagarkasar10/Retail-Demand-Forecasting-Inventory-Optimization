import pandas as pd
import pytest

from src.dashboard.price_scenario_service import (
    apply_price_scenario,
    calculate_new_price,
    calculate_demand_multiplier,
)


@pytest.fixture
def forecast_df():
    return pd.DataFrame(
        {
            "forecast_date": pd.date_range(
                start="2026-09-01",
                periods=3,
                freq="D",
            ),
            "predicted_demand": [100, 120, 140],
        }
    )


def test_calculate_new_price():
    result = calculate_new_price(
        base_price=100,
        price_change_percent=-10,
    )

    assert result == 90


def test_calculate_demand_multiplier():
    result = calculate_demand_multiplier(
        price_change_percent=-10,
        elasticity=-1.5,
    )

    assert result == 1.15


def test_apply_price_scenario(forecast_df):
    result = apply_price_scenario(
        forecast_df=forecast_df,
        base_price=100,
        price_change_percent=-10,
        elasticity=-1.0,
    )

    assert "scenario_price" in result.columns
    assert "scenario_demand" in result.columns
    assert "base_revenue" in result.columns
    assert "scenario_revenue" in result.columns

    assert result["scenario_price"].iloc[0] == 90
    assert result["scenario_demand"].iloc[0] == pytest.approx(110)


def test_price_reduction_increases_demand(forecast_df):
    result = apply_price_scenario(
        forecast_df=forecast_df,
        base_price=100,
        price_change_percent=-20,
        elasticity=-1.0,
    )

    assert (
        result["scenario_demand"]
        >= result["base_demand"]
    ).all()


def test_invalid_base_price(forecast_df):
    with pytest.raises(ValueError):
        apply_price_scenario(
            forecast_df=forecast_df,
            base_price=0,
            price_change_percent=-10,
            elasticity=-1.0,
        )
