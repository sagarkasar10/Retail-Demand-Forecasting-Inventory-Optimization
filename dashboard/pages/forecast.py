"""
Demand Forecast dashboard page.

Provides store, department, category, item, model,
and date filters and displays a 30-day demand forecast.
"""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import streamlit as st

from src.dashboard.data_access import (
    get_available_categories,
    get_available_departments,
    get_available_items,
    get_available_models,
    get_available_stores,
    get_forecast_data,
)


def _safe_list(loader) -> list[str]:
    """
    Safely load filter options.
    """
    try:
        return loader()
    except Exception as exc:
        st.warning(
            f"Unable to load filter options: {exc}"
        )
        return []


def _prepare_forecast_chart(
    forecast_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Aggregate forecast demand by date.
    """
    if forecast_df.empty:
        return pd.DataFrame()

    chart_df = (
        forecast_df
        .groupby(
            "forecast_date",
            as_index=False,
        )["predicted_demand"]
        .sum()
        .sort_values("forecast_date")
    )

    return chart_df.set_index("forecast_date")


def render_forecast() -> None:
    """
    Render the demand forecast page.
    """
    st.title("Demand Forecast")

    st.markdown(
        """
        Select a store, product hierarchy, model, and forecast
        period to analyze expected demand.
        """
    )

    stores = _safe_list(get_available_stores)
    departments = _safe_list(
        get_available_departments
    )
    categories = _safe_list(
        get_available_categories
    )
    items = _safe_list(get_available_items)
    models = _safe_list(get_available_models)

    col1, col2, col3 = st.columns(3)

    with col1:
        store_id = st.selectbox(
            "Store",
            ["All"] + stores,
        )

    with col2:
        dept_id = st.selectbox(
            "Department",
            ["All"] + departments,
        )

    with col3:
        cat_id = st.selectbox(
            "Category",
            ["All"] + categories,
        )

    col4, col5 = st.columns(2)

    with col4:
        item_id = st.selectbox(
            "Item",
            ["All"] + items,
        )

    with col5:
        model_name = st.selectbox(
            "Forecast Model",
            ["All"] + models,
        )

    st.subheader("Forecast Period")

    today = date.today()

    start_date = st.date_input(
        "Start Date",
        value=today,
        key="forecast_start_date",
    )

    end_date = st.date_input(
        "End Date",
        value=today + timedelta(days=29),
        key="forecast_end_date",
    )

    if start_date > end_date:
        st.error(
            "Start date cannot be after end date."
        )
        return

    if (end_date - start_date).days > 30:
        st.warning(
            "The dashboard is designed for a maximum "
            "30-day forecast view."
        )

    if st.button(
        "Load Forecast",
        type="primary",
    ):
        try:
            forecast_df = get_forecast_data(
                store_id=(
                    None
                    if store_id == "All"
                    else store_id
                ),
                dept_id=(
                    None
                    if dept_id == "All"
                    else dept_id
                ),
                cat_id=(
                    None
                    if cat_id == "All"
                    else cat_id
                ),
                item_id=(
                    None
                    if item_id == "All"
                    else item_id
                ),
                model_name=(
                    None
                    if model_name == "All"
                    else model_name
                ),
                start_date=str(start_date),
                end_date=str(end_date),
            )

            if forecast_df.empty:
                st.warning(
                    "No forecast data found for the selected filters."
                )
                return

            total_demand = (
                forecast_df["predicted_demand"]
                .sum()
            )

            average_daily_demand = (
                forecast_df
                .groupby("forecast_date")
                ["predicted_demand"]
                .sum()
                .mean()
            )

            peak_day = (
                forecast_df
                .groupby("forecast_date")
                ["predicted_demand"]
                .sum()
                .idxmax()
            )

            peak_demand = (
                forecast_df
                .groupby("forecast_date")
                ["predicted_demand"]
                .sum()
                .max()
            )

            metric_col1, metric_col2, metric_col3 = (
                st.columns(3)
            )

            with metric_col1:
                st.metric(
                    "Total Forecast Demand",
                    f"{total_demand:,.0f}",
                )

            with metric_col2:
                st.metric(
                    "Average Daily Demand",
                    f"{average_daily_demand:,.0f}",
                )

            with metric_col3:
                st.metric(
                    "Peak Demand",
                    f"{peak_demand:,.0f}",
                    help=f"Peak date: {peak_day}",
                )

            st.subheader("30-Day Demand Forecast")

            chart_df = _prepare_forecast_chart(
                forecast_df
            )

            st.line_chart(
                chart_df["predicted_demand"],
                use_container_width=True,
            )

            st.subheader("Forecast Details")

            display_columns = [
                "forecast_date",
                "store_id",
                "item_id",
                "dept_id",
                "cat_id",
                "model_name",
                "predicted_demand",
                "actual_demand",
            ]

            available_columns = [
                column
                for column in display_columns
                if column in forecast_df.columns
            ]

            st.dataframe(
                forecast_df[available_columns],
                use_container_width=True,
                hide_index=True,
            )

        except Exception as exc:
            st.error(
                "Unable to load demand forecast."
            )
            st.exception(exc)
