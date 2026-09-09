"""
Overview page for the Retail Demand Forecasting dashboard.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.dashboard.data_access import (
    get_forecast_data,
    get_latest_forecast_run,
)


def _calculate_kpis(df: pd.DataFrame) -> dict:
    """
    Calculate high-level dashboard KPIs from forecast data.
    """
    if df.empty:
        return {
            "forecast_items": 0,
            "forecast_units": 0.0,
            "stores": 0,
            "departments": 0,
        }

    return {
        "forecast_items": df["item_id"].nunique(),
        "forecast_units": df["predicted_demand"].sum(),
        "stores": df["store_id"].nunique(),
        "departments": df["dept_id"].nunique(),
    }


def render_overview() -> None:
    """
    Render the dashboard overview page.
    """
    st.title("Retail Demand Forecasting & Inventory Optimization")

    st.markdown(
        """
        Monitor forecasted demand, stores, products, and model-generated
        predictions from the centralized BigQuery forecasting layer.
        """
    )

    try:
        forecast_df = get_latest_forecast_run()

    except Exception as exc:
        st.error(
            "Unable to load forecast data from BigQuery."
        )
        st.exception(exc)
        return

    if forecast_df.empty:
        st.warning(
            "No forecast data is currently available."
        )
        return

    kpis = _calculate_kpis(forecast_df)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Forecast Items",
            f"{kpis['forecast_items']:,}",
        )

    with col2:
        st.metric(
            "Forecast Units",
            f"{kpis['forecast_units']:,.0f}",
        )

    with col3:
        st.metric(
            "Stores",
            f"{kpis['stores']:,}",
        )

    with col4:
        st.metric(
            "Departments",
            f"{kpis['departments']:,}",
        )

    st.divider()

    st.subheader("Forecast Demand Trend")

    trend_df = (
        forecast_df
        .groupby("forecast_date", as_index=False)["predicted_demand"]
        .sum()
        .sort_values("forecast_date")
    )

    trend_df = trend_df.set_index("forecast_date")

    st.line_chart(
        trend_df["predicted_demand"],
        use_container_width=True,
    )

    st.subheader("Top Items by Forecasted Demand")

    top_items = (
        forecast_df
        .groupby(
            ["item_id"],
            as_index=False,
        )["predicted_demand"]
        .sum()
        .sort_values(
            "predicted_demand",
            ascending=False,
        )
        .head(10)
    )

    st.dataframe(
        top_items,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Latest Forecast")

    display_columns = [
        "forecast_date",
        "store_id",
        "item_id",
        "dept_id",
        "cat_id",
        "model_name",
        "predicted_demand",
    ]

    available_columns = [
        column
        for column in display_columns
        if column in forecast_df.columns
    ]

    st.dataframe(
        forecast_df[available_columns].head(50),
        use_container_width=True,
        hide_index=True,
    )
