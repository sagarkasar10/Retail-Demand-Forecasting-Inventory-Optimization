import streamlit as st

from src.dashboard.data_access import (
    get_available_stores,
    get_available_items,
    get_forecast_data,
)

from src.dashboard.inventory_service import (
    calculate_inventory_metrics,
    calculate_item_inventory_status,
)


def render_inventory():
    st.title("Inventory Optimization")

    st.write(
        "Estimate reorder requirements and projected inventory "
        "levels using forecasted demand."
    )

    try:
        stores = get_available_stores()

        if not stores:
            st.warning("No stores are available.")
            return

        selected_store = st.selectbox(
            "Store",
            stores
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
            items
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

        with st.spinner("Calculating inventory requirements..."):
            forecast_df = get_forecast_data(
                store_id=selected_store,
                item_id=selected_item,
            )

        if forecast_df.empty:
            st.warning(
                "No forecast data found for the selected item."
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

        if metrics["stockout_risk"]:
            st.error(
                "High stockout risk: current stock is below "
                "the calculated reorder point."
            )
        else:
            st.success(
                "Current stock is above the calculated "
                "reorder point."
            )

        inventory_projection = calculate_item_inventory_status(
            forecast_df,
            metrics,
        )

        st.subheader("Projected Inventory")

        st.line_chart(
            inventory_projection.set_index(
                "forecast_date"
            )["projected_stock"]
        )

        st.subheader("Daily Inventory Projection")

        st.dataframe(
            inventory_projection,
            use_container_width=True,
            hide_index=True,
        )

        csv_data = inventory_projection.to_csv(
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

        with st.expander("Technical details"):
            st.exception(exc)