"""
Inventory optimization dashboard page.

Displays inventory KPIs, stockout risk,
recommended order quantities, and inventory
status by store and item.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd

from src.dashboard.inventory_service import (
    calculate_item_inventory_status,
    create_inventory_summary,
)


def render_inventory_page(
    forecast_df: pd.DataFrame,
    inventory_df: pd.DataFrame,
) -> None:
    """
    Render the inventory optimization dashboard.
    """

    st.title("Inventory Optimization")

    st.write(
        "Analyze forecast-based inventory requirements, "
        "stockout risk, and recommended replenishment."
    )

    if forecast_df is None or forecast_df.empty:
        st.warning(
            "No forecast data is available for inventory optimization."
        )
        return

    if inventory_df is None or inventory_df.empty:
        st.warning(
            "No inventory data is available."
        )
        return

    # ---------------------------------------------------------
    # Sidebar configuration
    # ---------------------------------------------------------

    st.sidebar.subheader("Inventory Parameters")

    lead_time_days = st.sidebar.number_input(
        "Lead Time (Days)",
        min_value=1,
        max_value=90,
        value=7,
        step=1,
    )

    safety_stock_days = st.sidebar.number_input(
        "Safety Stock (Days)",
        min_value=0.0,
        max_value=30.0,
        value=3.0,
        step=0.5,
    )

    # ---------------------------------------------------------
    # Validate forecast columns
    # ---------------------------------------------------------

    required_forecast_columns = {
        "store_id",
        "item_id",
        "predicted_demand",
    }

    missing_forecast_columns = (
        required_forecast_columns
        - set(forecast_df.columns)
    )

    if missing_forecast_columns:
        st.error(
            "Forecast data is missing required columns: "
            f"{sorted(missing_forecast_columns)}"
        )
        return

    # ---------------------------------------------------------
    # Calculate inventory status
    # ---------------------------------------------------------

    try:
        inventory_status_df = (
            calculate_item_inventory_status(
                forecast_df=forecast_df,
                inventory_df=inventory_df,
                lead_time_days=lead_time_days,
                safety_stock_days=safety_stock_days,
            )
        )

    except ValueError as exc:
        st.error(str(exc))
        return

    if inventory_status_df.empty:
        st.warning(
            "No matching store-item inventory records "
            "were found."
        )
        return

    # ---------------------------------------------------------
    # Calculate summary KPIs
    # ---------------------------------------------------------

    summary = create_inventory_summary(
        inventory_status_df
    )

    # ---------------------------------------------------------
    # KPI cards
    # ---------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Items",
            f"{summary['total_items']:,}",
        )

    with col2:
        st.metric(
            "Stockout Risk",
            f"{summary['stockout_risk_items']:,}",
        )

    with col3:
        st.metric(
            "Recommended Units",
            f"{summary['total_recommended_units']:,.0f}",
        )

    with col4:
        st.metric(
            "Average Coverage",
            f"{summary['average_coverage']:.1f} days",
        )

    st.divider()

    # ---------------------------------------------------------
    # Filters
    # ---------------------------------------------------------

    st.subheader("Inventory Filters")

    filter_col1, filter_col2 = st.columns(2)

    filtered_df = inventory_status_df.copy()

    with filter_col1:

        store_options = sorted(
            filtered_df["store_id"]
            .astype(str)
            .unique()
            .tolist()
        )

        selected_stores = st.multiselect(
            "Select Store",
            options=store_options,
            default=store_options,
        )

        if selected_stores:
            filtered_df = filtered_df[
                filtered_df["store_id"]
                .astype(str)
                .isin(selected_stores)
            ]

    with filter_col2:

        risk_filter = st.selectbox(
            "Stockout Risk",
            options=[
                "All",
                "At Risk",
                "Safe",
            ],
        )

        if risk_filter == "At Risk":
            filtered_df = filtered_df[
                filtered_df["stockout_risk"] == True
            ]

        elif risk_filter == "Safe":
            filtered_df = filtered_df[
                filtered_df["stockout_risk"] == False
            ]

    # ---------------------------------------------------------
    # Inventory status table
    # ---------------------------------------------------------

    st.subheader("Inventory Status")

    display_columns = [
        "store_id",
        "item_id",
        "current_stock",
        "forecast_demand",
        "average_daily_demand",
        "lead_time_demand",
        "safety_stock",
        "reorder_point",
        "recommended_order_quantity",
        "stockout_risk",
    ]

    available_columns = [
        column
        for column in display_columns
        if column in filtered_df.columns
    ]

    display_df = filtered_df[
        available_columns
    ].copy()

    numeric_columns = [
        "current_stock",
        "forecast_demand",
        "average_daily_demand",
        "lead_time_demand",
        "safety_stock",
        "reorder_point",
        "recommended_order_quantity",
    ]

    for column in numeric_columns:

        if column in display_df.columns:
            display_df[column] = display_df[
                column
            ].round(2)

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )

    # ---------------------------------------------------------
    # Replenishment recommendations
    # ---------------------------------------------------------

    st.subheader("Replenishment Recommendations")

    replenishment_df = filtered_df[
        filtered_df[
            "recommended_order_quantity"
        ] > 0
    ].copy()

    if replenishment_df.empty:

        st.success(
            "No replenishment is currently recommended "
            "for the selected filters."
        )

    else:

        replenishment_columns = [
            "store_id",
            "item_id",
            "current_stock",
            "reorder_point",
            "recommended_order_quantity",
            "stockout_risk",
        ]

        replenishment_df = replenishment_df[
            replenishment_columns
        ].sort_values(
            "recommended_order_quantity",
            ascending=False,
        )

        st.dataframe(
            replenishment_df,
            use_container_width=True,
            hide_index=True,
        )

    # ---------------------------------------------------------
    # Stockout risk chart
    # ---------------------------------------------------------

    st.subheader("Stockout Risk by Store")

    risk_by_store = (
        filtered_df
        .groupby("store_id")["stockout_risk"]
        .sum()
        .sort_values(ascending=False)
    )

    if not risk_by_store.empty:

        st.bar_chart(
            risk_by_store,
            use_container_width=True,
        )

    # ---------------------------------------------------------
    # Recommended order quantity chart
    # ---------------------------------------------------------

    st.subheader(
        "Recommended Order Quantity by Store"
    )

    order_by_store = (
        filtered_df
        .groupby("store_id")[
            "recommended_order_quantity"
        ]
        .sum()
        .sort_values(ascending=False)
    )

    if not order_by_store.empty:

        st.bar_chart(
            order_by_store,
            use_container_width=True,
        )

    # ---------------------------------------------------------
    # Download recommendations
    # ---------------------------------------------------------

    st.subheader("Export Recommendations")

    csv_data = replenishment_df.to_csv(
        index=False
    )

    st.download_button(
        label="Download Replenishment Recommendations",
        data=csv_data,
        file_name="inventory_replenishment_recommendations.csv",
        mime="text/csv",
    )


# -------------------------------------------------------------
# Streamlit entry point
# -------------------------------------------------------------

def main() -> None:
    """
    Standalone entry point.

    The main dashboard should normally call
    render_inventory_page() with forecast and
    inventory data.
    """

    st.info(
        "Load forecast and inventory data from "
        "the main dashboard to view inventory optimization."
    )


if __name__ == "__main__":
    main()