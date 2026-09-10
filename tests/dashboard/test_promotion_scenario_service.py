import pandas as pd
import pytest

from src.dashboard.promotion_scenario_service import (
    apply_promotion_scenario,
    get_promotion_scenario_summary,
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
            "predicted_demand": [100, 200, 300],
        }
    )


def test_apply_promotion_scenario(forecast_df):
    result = apply_promotion_scenario(
        forecast_df=forecast_df,
        promotion_lift_percent=10,
    )

    assert "base_demand" in result.columns
    assert "scenario_demand" in result.columns
    assert "additional_demand" in result.columns

    assert result["scenario_demand"].iloc[0] == pytest.approx(110)
    assert result["additional_demand"].iloc[0] == pytest.approx(10)


def test_promotion_increases_demand(forecast_df):
    result = apply_promotion_scenario(
        forecast_df=forecast_df,
        promotion_lift_percent=25,
    )

    assert (
        result["scenario_demand"]
        >= result["base_demand"]
    ).all()


def test_promotion_summary(forecast_df):
    scenario_df = apply_promotion_scenario(
        forecast_df=forecast_df,
        promotion_lift_percent=10,
    )

    summary = get_promotion_scenario_summary(
        scenario_df
    )

    assert summary["base_demand"] == 600
    assert summary["scenario_demand"] == 660
    assert summary["additional_demand"] == 60
    assert summary["demand_change_percent"] == 10


def test_invalid_promotion_lift(forecast_df):
    with pytest.raises(ValueError):
        apply_promotion_scenario(
            forecast_df=forecast_df,
            promotion_lift_percent=-101,
        )
