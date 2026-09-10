import math

import pandas as pd
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
    create_inventory_summary,
)


def render_inventory() -> None:
    """
    Render the Inventory Optimization Streamlit page.

    The page loads the final forecast data and passes it to
    inventory_service.py for all inventory calculations.
    """

    st.title("Inventory Optimization")

    st.write(
        "Estimate reorder requirements, stockout risk, "
        "inventory coverage, and projected inventory levels "
        "using the final forecast data."
    )

    try:

        # --------------------------------------------------
        # Store selection
        # --------------------------------------------------

        stores = get_available_stores()

        if not stores:
            st.warning(
                "No stores are available."
            )
            return

        selected_store = st.selectbox(
            "Store",
            stores,
            key="inventory_store",
        )

        # --------------------------------------------------
        # Item selection
        # --------------------------------------------------

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
            key="inventory_item",
        )

        # --------------------------------------------------
        # Inventory parameters
        # --------------------------------------------------

        st.subheader(
            "Inventory Parameters"
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
                max_value=365,
                value=7,
                step=1,
            )

        with col3:
            safety_stock_days = st.number_input(
                "Safety Stock (Days)",
                min_value=0.0,
                max_value=365.0,
                value=3.0,
                step=0.5,
            )

        # --------------------------------------------------
        # Calculate button
        # --------------------------------------------------

        if not st.button(
            "Calculate Inventory",
            type="primary",
            use_container_width=True,
        ):
            return

        # --------------------------------------------------
        # Load final forecast data
        # --------------------------------------------------

        with st.spinner(
            "Loading final forecast data..."
        ):

            forecast_df = get_forecast_data(
                store_id=selected_store,
                item_id=selected_item,
            )

        if (
            forecast_df is None
            or forecast_df.empty
        ):
            st.warning(
                "No forecast data was found for the "
                "selected store and item."
            )
            return

        required_columns = {
            "forecast_date",
            "predicted_demand",
        }

        missing_columns = (
            required_columns -
            set(forecast_df.columns)
        )

        if missing_columns:
            st.error(
                "The final forecast data is missing "
                f"required columns: {sorted(missing_columns)}"
            )
            return

        # --------------------------------------------------
        # Calculate inventory metrics
        # --------------------------------------------------

        metrics = calculate_inventory_metrics(
            forecast_df=forecast_df,
            current_stock=current_stock,
            lead_time_days=lead_time_days,
            safety_stock_days=safety_stock_days,
        )

        alert = calculate_inventory_alert(
            metrics
        )

        # --------------------------------------------------
        # KPI section
        # --------------------------------------------------

        st.subheader(
            "Inventory KPIs"
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Current Stock",
            f"{metrics['current_stock']:,.0f}",
        )

        col2.metric(
            "Average Daily Demand",
            f"{metrics['average_daily_demand']:,.2f}",
        )

        col3.metric(
            "Reorder Point",
            f"{metrics['reorder_point']:,.2f}",
        )

        col4.metric(
            "Recommended Order",
            f"{metrics['recommended_order_quantity']:,.0f}",
        )

        col5, col6, col7 = st.columns(3)

        days_of_stock = (
            metrics["days_of_stock"]
        )

        days_of_stock_display = (
            "Unlimited"
            if math.isinf(days_of_stock)
            else f"{days_of_stock:.2f} days"
        )

        col5.metric(
            "Safety Stock",
            f"{metrics['safety_stock']:,.2f}",
        )

        col6.metric(
            "Days of Stock",
            days_of_stock_display,
        )

        col7.metric(
            "Forecast Horizon",
            f"{metrics['forecast_horizon_days']} days",
        )

        # --------------------------------------------------
        # Inventory alert
        # --------------------------------------------------

        st.subheader(
            "Inventory Risk Status"
        )

        if alert == "CRITICAL":

            st.error(
                "CRITICAL: Current inventory is zero. "
                "Immediate replenishment is required."
            )

        elif alert == "HIGH":

            st.error(
                "HIGH RISK: Current inventory is at or "
                "below the reorder point."
            )

        elif alert == "MEDIUM":

            st.warning(
                "MEDIUM RISK: Inventory coverage should "
                "be monitored closely."
            )

        else:

            st.success(
                "LOW RISK: Current inventory coverage is "
                "sufficient."
            )

        # --------------------------------------------------
        # Calculation details
        # --------------------------------------------------

        st.subheader(
            "Inventory Calculation Summary"
        )

        summary_df = create_inventory_summary(
            metrics
        )

        st.dataframe(
            summary_df,
            use_container_width=True,
            hide_index=True,
        )

        # --------------------------------------------------
        # Inventory projection
        # --------------------------------------------------

        projection = (
            calculate_item_inventory_status(
                forecast_df=forecast_df,
                inventory_data=metrics,
            )
        )

        st.subheader(
            "Projected Inventory"
        )

        chart_df = projection.set_index(
            "forecast_date"
        )[
            "projected_stock"
        ]

        st.line_chart(
            chart_df,
            use_container_width=True,
        )

        # --------------------------------------------------
        # Stockout information
        # --------------------------------------------------

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
                "the available forecast horizon."
            )

        # --------------------------------------------------
        # Projection details
        # --------------------------------------------------

        st.subheader(
            "Daily Inventory Projection"
        )

        display_projection = projection.copy()

        numeric_columns = [
            "predicted_demand",
            "cumulative_forecast_demand",
            "projected_stock",
        ]

        for column in numeric_columns:

            if column in display_projection.columns:

                display_projection[column] = (
                    display_projection[column]
                    .round(2)
                )

        st.dataframe(
            display_projection,
            use_container_width=True,
            hide_index=True,
        )

        # --------------------------------------------------
        # Download projection
        # --------------------------------------------------

        st.subheader(
            "Export Inventory Projection"
        )

        csv_data = (
            projection.to_csv(
                index=False
            )
            .encode("utf-8")
        )

        st.download_button(
            "Download Inventory Projection",
            data=csv_data,
            file_name=(
                "inventory_projection_"
                f"{selected_store}_{selected_item}.csv"
            ),
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