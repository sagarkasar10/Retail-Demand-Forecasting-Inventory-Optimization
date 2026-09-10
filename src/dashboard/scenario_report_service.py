from datetime import datetime
from typing import Dict

import pandas as pd


def generate_scenario_summary(
    scenario_df: pd.DataFrame,
    inventory_metrics: Dict[str, float],
    scenario_type: str,
) -> Dict[str, object]:
    """Generate a complete scenario analysis summary."""

    if scenario_df.empty:
        raise ValueError(
            "Scenario data cannot be empty."
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

    demand_change_percent = (
        demand_difference /
        base_demand *
        100
        if base_demand > 0
        else 0.0
    )

    summary = {
        "scenario_type": scenario_type,
        "generated_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "forecast_start_date": str(
            pd.to_datetime(
                scenario_df["forecast_date"]
            ).min().date()
        ),
        "forecast_end_date": str(
            pd.to_datetime(
                scenario_df["forecast_date"]
            ).max().date()
        ),
        "base_demand": base_demand,
        "scenario_demand": scenario_demand,
        "demand_difference": demand_difference,
        "demand_change_percent": demand_change_percent,
        "current_stock": inventory_metrics[
            "current_stock"
        ],
        "reorder_point": inventory_metrics[
            "reorder_point"
        ],
        "recommended_order_quantity": (
            inventory_metrics[
                "recommended_order_quantity"
            ]
        ),
        "days_of_stock": inventory_metrics[
            "days_of_stock"
        ],
        "stockout_risk": inventory_metrics[
            "stockout_risk"
        ],
    }

    if "base_revenue" in scenario_df.columns:
        summary["base_revenue"] = float(
            scenario_df["base_revenue"].sum()
        )

    if "scenario_revenue" in scenario_df.columns:
        summary["scenario_revenue"] = float(
            scenario_df["scenario_revenue"].sum()
        )

        summary["revenue_difference"] = (
            summary["scenario_revenue"]
            - summary["base_revenue"]
        )

        summary["revenue_change_percent"] = (
            summary["revenue_difference"]
            / summary["base_revenue"]
            * 100
            if summary["base_revenue"] > 0
            else 0.0
        )

    return summary


def create_scenario_report_dataframe(
    summary: Dict[str, object],
) -> pd.DataFrame:
    """Convert scenario summary into report format."""

    report_rows = []

    for metric, value in summary.items():
        report_rows.append(
            {
                "metric": metric,
                "value": value,
            }
        )

    return pd.DataFrame(report_rows)


def create_scenario_filename(
    scenario_type: str,
) -> str:
    """Create a timestamped scenario report filename."""

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    scenario_name = (
        scenario_type.lower()
        .replace(" ", "_")
    )

    return (
        f"{scenario_name}_scenario_"
        f"{timestamp}.csv"
    )