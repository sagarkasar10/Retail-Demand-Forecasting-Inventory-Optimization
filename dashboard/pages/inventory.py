"""
Inventory optimization dashboard page.
"""

from __future__ import annotations

import streamlit as st

from src.dashboard.data_access import (
    get_forecast_data,
)
from src.dashboard.inventory_service import (
    calculate_inventory_metrics,
)


def render_inventory() -> None:
    """
    Render inventory optimization page.
    """
    st.title("Inventory Optimization")

    st.markdown(
        """
        Estimate reorder points and recommended order quantities
        from forecasted demand.
        """
    )

    col1, col2 = st.columns(2)

    with col1:
        store_id = st.text_input(
            "Store ID",
            placeholder="CA_1",
        )

    with col2:
        item_id = st.text_input(
            "Item ID",
            placeholder="FOODS_1_001",
        )

    col3, col4, col5 = st.columns(3)

    with col3:
        current_stock = st.number_input(
            "Current Stock",
            min_value=0.0,
            value=100.0,
            step=1.0,
        )

    with col4:
        lead_time_days = st.number_input(
            "Lead Time (Days)",
            min_value=1,
            value=7,
            step=1,
        )

    with col5:
        safety_stock_days = st.number_input(
            "Safety Stock (Days)",
            min_value=0,
            value=3,
            step=1,
        )

    if st.button(
        "Calculate",
        type="primary",
    ):
        if not store_id or not item_id:
            st.error(
                "Store ID and Item ID are required."
            )
            return

        try:
            forecast_df = get_forecast_data(
                store_id=store_id,
                item_id=item_id,
            )

            if forecast_df.empty:
                st.warning(
                    "No forecast data found."
                )
                return

            metrics = calculate_inventory_metrics(
                forecast_df=forecast_df,
                current_stock=current_stock,
                lead_time_days=lead_time_days,
                safety_stock_days=safety_stock_days,
            )

            st.subheader("Inventory KPIs")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Average Daily Demand",
                    f"{metrics['average_daily_demand']:,.1f}",
                )

            with col2:
                st.metric(
                    "Lead-Time Demand",
                    f"{metrics['lead_time_demand']:,.1f}",
                )

            with col3:
                st.metric(
                    "Reorder Point",
                    f"{metrics['reorder_point']:,.1f}",
                )

            with col4:
                st.metric(
                    "Recommended Order",
                    f"{metrics['recommended_order_quantity']:,.1f}",
                )

            st.divider()

            if metrics["stockout_risk"]:
                st.error(
                    "HIGH PRIORITY: Current stock may not cover "
                    "expected lead-time demand."
                )
            else:
                st.success(
                    "Current stock covers estimated lead-time demand."
                )

            st.subheader("Demand vs Current Stock")

            chart_data = {
                "Current Stock": current_stock,
                "Lead-Time Demand": (
                    metrics["lead_time_demand"]
                ),
                "Safety Stock": (
                    metrics["safety_stock"]
                ),
                "Reorder Point": (
                    metrics["reorder_point"]
                ),
            }

            st.bar_chart(
                chart_data,
                use_container_width=True,
            )

            st.subheader("Calculation Details")

            st.dataframe(
                [
                    {
                        "Metric": "Forecast Demand",
                        "Value": metrics[
                            "forecast_demand"
                        ],
                    },
                    {
                        "Metric": "Average Daily Demand",
                        "Value": metrics[
                            "average_daily_demand"
                        ],
                    },
                    {
                        "Metric": "Lead-Time Demand",
                        "Value": metrics[
                            "lead_time_demand"
                        ],
                    },
                    {
                        "Metric": "Safety Stock",
                        "Value": metrics[
                            "safety_stock"
                        ],
                    },
                    {
                        "Metric": "Reorder Point",
                        "Value": metrics[
                            "reorder_point"
                        ],
                    },
                    {
                        "Metric": "Recommended Order Quantity",
                        "Value": metrics[
                            "recommended_order_quantity"
                        ],
                    },
                ],
            )

        except Exception as exc:
            st.error(
                "Unable to calculate inventory recommendation."
            )
            st.exception(exc)