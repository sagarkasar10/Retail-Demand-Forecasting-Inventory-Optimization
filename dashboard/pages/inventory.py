import math

import streamlit as st

from src.dashboard.data_access import (
    get_available_stores,
    get_available_items,
    get_forecast_data,
)

from src.dashboard.inventory_service import (
    calculate_inventory_metrics,
    calculate_item_inventory_status,
    calculate_inventory_alert,
)


def render_inventory():
    st.title("Inventory Optimization")

    st.write(
        "Estimate reorder requirements, stockout risk, "
        "and projected inventory levels."
    )

    try:
        stores = get_available_stores()

        if not stores:
            st.warning(
                "No stores are available."
            )
            return

        selected_store = st.selectbox(
            "Store",
            stores,
            key="inventory_store"
        )

        items = get_available_items(
            store_id=selected_store
        )

        if not items:
            st.warning(
                "No items are available for the selected store."
            )
            return

        selected_item = st.selectbox(
            "Item",
            items,
            key="inventory_item"
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            current_stock = st.number_input(
                "Current Stock",
                min_value=0.0,
                value=100.0,
                step=1.0,
            )

        with col2:
            lead_time_days = st.number_input(
                "Lead Time (Days)",
                min_value=1,
                value=7,
                step=1,
            )

        with col3:
            safety_stock_days = st.number_input(
                "Safety Stock (Days)",
                min_value=0.0,
                value=3.0,
                step=0.5,
            )

        if not st.button(
            "Calculate Inventory",
            type="primary",
            use_container_width=True,
        ):
            return

        with st.spinner(
            "Loading forecast data..."
        ):
            forecast_df = get_forecast_data(
                store_id=selected_store,
                item_id=selected_item,
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

        alert = calculate_inventory_alert(
            metrics
        )

        st.subheader(
            "Inventory KPIs"
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Current Stock",
            f"{metrics['current_stock']:,.0f}"
        )

        col2.metric(
            "Daily Demand",
            f"{metrics['average_daily_demand']:,.2f}"
        )

        col3.metric(
            "Reorder Point",
            f"{metrics['reorder_point']:,.2f}"
        )

        col4.metric(
            "Recommended Order",
            f"{metrics['recommended_order_quantity']:,.0f}"
        )

        if alert == "CRITICAL":
            st.error(
                "CRITICAL: Current stock is zero."
            )

        elif alert == "HIGH":
            st.error(
                "HIGH RISK: Current stock is below "
                "the reorder point."
            )

        elif alert == "MEDIUM":
            st.warning(
                "MEDIUM RISK: Inventory coverage "
                "should be monitored."
            )

        else:
            st.success(
                "LOW RISK: Current inventory is "
                "above the reorder point."
            )

        projection = calculate_item_inventory_status(
            forecast_df,
            metrics,
        )

        st.subheader(
            "Projected Inventory"
        )

        chart_df = projection.set_index(
            "forecast_date"
        )[
            [
                "projected_stock",
            ]
        ]

        st.line_chart(
            chart_df
        )

        stockout_rows = projection[
            projection["stockout"]
        ]

        if not stockout_rows.empty:
            first_stockout_date = (
                stockout_rows.iloc[0][
                    "forecast_date"
                ]
            )

            st.warning(
                "Projected stockout date: "
                f"{first_stockout_date.date()}"
            )

        else:
            st.success(
                "No stockout is projected within "
                "the selected forecast horizon."
            )

        st.subheader(
            "Inventory Details"
        )

        st.dataframe(
            projection,
            use_container_width=True,
            hide_index=True,
        )

        csv_data = projection.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "Download Inventory Projection",
            data=csv_data,
            file_name="inventory_projection.csv",
            mime="text/csv",
            use_container_width=True,
        )

    except ValueError as exc:
        st.error(str(exc))

    except Exception as exc:
        st.error(
            "Unable to calculate inventory requirements."
        )

        with st.expander(
            "Technical details"
        ):
            st.exception(exc)