import pandas as pd
import pytest

from src.dashboard.scenario_inventory_service import (
    calculate_scenario_inventory_impact,
    create_scenario_stock_projection,
)


@pytest.fixture
def scenario_df():
    return pd.DataFrame(
        {
            "forecast_date": pd.date_range(
                start="2026-09-01",
                periods=5,
                freq="D",
            ),
            "scenario_demand": [
                100,
                120,
                110,
                130,
                140,
            ],
        }
    )


def test_calculate_inventory_impact(scenario_df):
    result = calculate_scenario_inventory_impact(
        scenario_df=scenario_df,
        current_stock=500,
        lead_time_days=3,
        safety_stock_days=2,
    )

    assert "reorder_point" in result
    assert "recommended_order_quantity" in result
    assert "days_of_stock" in result
    assert "stockout_risk" in result

    assert result["average_daily_demand"] == 120


def test_inventory_reorder_recommendation(scenario_df):
    result = calculate_scenario_inventory_impact(
        scenario_df=scenario_df,
        current_stock=100,
        lead_time_days=3,
        safety_stock_days=2,
    )

    assert result["recommended_order_quantity"] > 0
    assert result["stockout_risk"] is True


def test_stock_projection(scenario_df):
    result = create_scenario_stock_projection(
        scenario_df=scenario_df,
        current_stock=1000,
    )

    assert "forecast_date" in result.columns
    assert "scenario_demand" in result.columns
    assert "projected_stock" in result.columns
    assert "stockout" in result.columns

    assert result["projected_stock"].iloc[0] == 900


def test_negative_stock_not_allowed(scenario_df):
    with pytest.raises(ValueError):
        calculate_scenario_inventory_impact(
            scenario_df=scenario_df,
            current_stock=-100,
            lead_time_days=3,
            safety_stock_days=2,
        )


def test_invalid_lead_time(scenario_df):
    with pytest.raises(ValueError):
        calculate_scenario_inventory_impact(
            scenario_df=scenario_df,
            current_stock=500,
            lead_time_days=0,
            safety_stock_days=2,
        )
        