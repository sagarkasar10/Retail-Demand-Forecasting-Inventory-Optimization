"""
Basic tests for Week 4 dashboard data-access utilities.

These tests do not require a live BigQuery connection.
"""

from src.dashboard.inventory_service import (
    calculate_inventory_metrics,
)

import pandas as pd


def test_inventory_calculation_with_forecast_data():
    """
    Verify basic inventory calculations.
    """
    forecast_df = pd.DataFrame(
        {
            "forecast_date": pd.to_datetime(
                [
                    "2026-09-01",
                    "2026-09-02",
                    "2026-09-03",
                ]
            ),
            "predicted_demand": [
                10.0,
                20.0,
                30.0,
            ],
        }
    )

    result = calculate_inventory_metrics(
        forecast_df=forecast_df,
        current_stock=20,
        lead_time_days=2,
        safety_stock_days=1,
    )

    assert result["total_forecast_demand"] == 60.0
    assert result["average_daily_demand"] == 20.0
    assert result["lead_time_demand"] == 40.0
    assert result["safety_stock"] == 20.0
    assert result["reorder_point"] == 60.0
    assert result["recommended_order_quantity"] == 40.0
    assert result["stockout_risk"] is True


def test_empty_forecast_returns_zero_metrics():
    """
    Verify that an empty forecast does not cause an exception.
    """
    forecast_df = pd.DataFrame(
        columns=[
            "forecast_date",
            "predicted_demand",
        ]
    )

    result = calculate_inventory_metrics(
        forecast_df=forecast_df,
        current_stock=100,
        lead_time_days=2,
        safety_stock_days=1,
    )

    assert result["total_forecast_demand"] == 0.0
    assert result["recommended_order_quantity"] == 0.0
    assert result["stockout_risk"] is False

