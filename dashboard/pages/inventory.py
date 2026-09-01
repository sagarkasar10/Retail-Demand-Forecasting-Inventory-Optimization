"""
Inventory dashboard page.

This page provides a basic inventory recommendation interface
using Week 3 forecast outputs.
"""

from __future__ import annotations

import streamlit as st

from src.dashboard.data_access import get_forecast_data
from src.dashboard.inventory_service import (
    calculate_inventory_metrics,
)


def render_inventory() -> None:
    """
    Render the inventory analysis page.
    """
    st.title("Inventory Optimization")

    st.markdown(
        """
        Use forecasted demand to estimate lead-time demand,
        safety stock, reorder point, and recommended replenishment.
        """
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        store_id = st.text_input(
            "Store ID",
            placeholder="e.g. CA_1",
        )

    with col2:
        item_id = st.text_input(
            "Item ID",
            placeholder="e.g. FOODS_1_001",
        )

    with col3:
        current_stock = st.number_input(
            "Current Stock",
            min_value=0.0,
            value=100.0,
            step=1.0,
        )

    col4, col5 = st.columns(2)

    with col4:
        lead_time_days = st.number_input(
            "Lead Time (days)",
            min_value=1,
            value=7,
            step=1,
        )

    with col5:
        safety_stock_days = st.number_input(
            "Safety Stock (days)",
            min_value=0,
            value=3,
            step=1,
        )

    if not store_id or not item_id:
        st.info(
            "Enter a Store ID and Item ID to calculate inventory recommendations."
        )
        return

    if st.button(
        "Calculate Inventory Recommendation",
        type="primary",
    ):
        try:
            forecast_df = get_forecast_data(
                store_id=store_id,
                item_id=item_id,
            )

            if forecast_df.empty:
                st.warning(
                    "No forecast data found for the selected store and item."
                )
                return

            metrics = calculate_inventory_metrics(
                forecast_df=forecast_df,
                current_stock=current_stock,
                lead_time_days=lead_time_days,
                safety_stock_days=safety_stock_days,
            )

            st.subheader("Inventory Summary")

            metric_col1, metric_col2, metric_col3 = st.columns(3)

            with metric_col1:
                st.metric(
                    "Forecast Demand",
                    f"{metrics['forecast_demand']:,.0f}",
                )

            with metric_col2:
                st.metric(
                    "Reorder Point",
                    f"{metrics['reorder_point']:,.0f}",
                )

            with metric_col3:
                st.metric(
                    "Recommended Order",
                    f"{metrics['recommended_order_quantity']:,.0f}",
                )

            if metrics["stockout_risk"]:
                st.warning(
                    "Stockout risk detected based on current stock "
                    "and estimated lead-time demand."
                )
            else:
                st.success(
                    "Current stock covers the estimated lead-time demand."
                )

            st.subheader("Inventory Calculation")

            st.write(
                {
                    "Current Stock": current_stock,
                    "Average Daily Demand": round(
                        metrics["average_daily_demand"],
                        2,
                    ),
                    "Lead-Time Demand": round(
                        metrics["lead_time_demand"],
                        2,
                    ),
                    "Safety Stock": round(
                        metrics["safety_stock"],
                        2,
                    ),
                    "Reorder Point": round(
                        metrics["reorder_point"],
                        2,
                    ),
                    "Recommended Order Quantity": round(
                        metrics["recommended_order_quantity"],
                        2,
                    ),
                }
            )

        except Exception as exc:
            st.error(
                "Unable to calculate inventory recommendation."
            )
            st.exception(exc)