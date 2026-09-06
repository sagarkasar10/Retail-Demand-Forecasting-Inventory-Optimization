import streamlit as st

from src.dashboard.data_access import (
    get_available_stores,
    get_available_items,
)

from src.dashboard.scenario_data_service import (
    get_scenario_base_data,
    get_historical_sales_for_scenario,
    get_latest_product_price,
)

from src.dashboard.price_scenario_service import (
    apply_price_scenario,
    get_price_scenario_summary,
)

from src.dashboard.promotion_scenario_service import (
    apply_promotion_scenario,
    get_promotion_scenario_summary,
)

from src.dashboard.scenario_inventory_service import (
    calculate_scenario_inventory_impact,
    create_scenario_stock_projection,
)


def render_price_scenario(
    forecast_df,
    base_price,
):
    st.subheader(
        "Price Change Scenario"
    )

    price_change_percent = st.slider(
        "Price Change (%)",
        min_value=-50.0,
        max_value=100.0,
        value=0.0,
        step=5.0,
        key="price_change_percent",
    )

    elasticity = st.number_input(
        "Price Elasticity",
        min_value=-10.0,
        max_value=0.0,
        value=-1.0,
        step=0.1,
        key="price_elasticity",
    )

    scenario_df = apply_price_scenario(
        forecast_df=forecast_df,
        base_price=base_price,
        price_change_percent=price_change_percent,
        elasticity=elasticity,
    )

    summary = get_price_scenario_summary(
        scenario_df
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Base Demand",
        f"{summary['base_demand']:,.0f}",
    )

    col2.metric(
        "Scenario Demand",
        f"{summary['scenario_demand']:,.0f}",
        delta=f"{summary['demand_change_percent']:.2f}%",
    )

    col3.metric(
        "Base Revenue",
        f"{summary['base_revenue']:,.2f}",
    )

    col4.metric(
        "Scenario Revenue",
        f"{summary['scenario_revenue']:,.2f}",
        delta=f"{summary['revenue_change_percent']:.2f}%",
    )

    chart_df = scenario_df[
        [
            "forecast_date",
            "base_demand",
            "scenario_demand",
        ]
    ].copy()

    chart_df = chart_df.set_index(
        "forecast_date"
    )

    st.line_chart(chart_df)

    return scenario_df


def render_promotion_scenario(
    forecast_df,
):
    st.subheader(
        "Promotion Scenario"
    )

    promotion_lift_percent = st.slider(
        "Expected Promotion Demand Lift (%)",
        min_value=0.0,
        max_value=200.0,
        value=10.0,
        step=5.0,
        key="promotion_lift_percent",
    )

    scenario_df = apply_promotion_scenario(
        forecast_df=forecast_df,
        promotion_lift_percent=promotion_lift_percent,
    )

    summary = get_promotion_scenario_summary(
        scenario_df
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Base Demand",
        f"{summary['base_demand']:,.0f}",
    )

    col2.metric(
        "Promotion Demand",
        f"{summary['scenario_demand']:,.0f}",
    )

    col3.metric(
        "Additional Demand",
        f"{summary['additional_demand']:,.0f}",
        delta=f"{summary['demand_change_percent']:.2f}%",
    )

    chart_df = scenario_df[
        [
            "forecast_date",
            "base_demand",
            "scenario_demand",
        ]
    ].copy()

    chart_df = chart_df.set_index(
        "forecast_date"
    )

    st.line_chart(chart_df)

    return scenario_df


def render_inventory_impact(
    scenario_df,
):
    st.subheader(
        "Inventory Impact"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        current_stock = st.number_input(
            "Current Stock",
            min_value=0.0,
            value=100.0,
            step=1.0,
            key="scenario_current_stock",
        )

    with col2:
        lead_time_days = st.number_input(
            "Lead Time (Days)",
            min_value=1,
            value=7,
            step=1,
            key="scenario_lead_time",
        )

    with col3:
        safety_stock_days = st.number_input(
            "Safety Stock Days",
            min_value=0.0,
            value=3.0,
            step=0.5,
            key="scenario_safety_stock",
        )

    inventory_metrics = (
        calculate_scenario_inventory_impact(
            scenario_df=scenario_df,
            current_stock=current_stock,
            lead_time_days=lead_time_days,
            safety_stock_days=safety_stock_days,
        )
    )

    metric1, metric2, metric3, metric4 = st.columns(4)

    metric1.metric(
        "Reorder Point",
        f"{inventory_metrics['reorder_point']:,.0f}",
    )

    metric2.metric(
        "Recommended Order",
        f"{inventory_metrics['recommended_order_quantity']:,.0f}",
    )

    metric3.metric(
        "Days of Stock",
        (
            "Unlimited"
            if inventory_metrics["days_of_stock"] == float("inf")
            else f"{inventory_metrics['days_of_stock']:.1f}"
        ),
    )

    metric4.metric(
        "Stockout Risk",
        (
            "High"
            if inventory_metrics["stockout_risk"]
            else "Low"
        ),
    )

    projection_df = (
        create_scenario_stock_projection(
            scenario_df=scenario_df,
            current_stock=current_stock,
        )
    )

    if not projection_df.empty:
        chart_df = projection_df.set_index(
            "forecast_date"
        )[["projected_stock"]]

        st.line_chart(chart_df)

    return inventory_metrics


def render_scenarios():
    st.title(
        "What-if Scenario Analysis"
    )

    st.write(
        "Simulate price changes and promotional demand "
        "uplift to understand their impact on demand, "
        "revenue, and inventory."
    )

    try:
        stores = get_available_stores()

        if not stores:
            st.warning(
                "No stores are available."
            )
            return

        selected_store = st.selectbox(
            "Select Store",
            stores,
            key="scenario_store",
        )

        items = get_available_items(
            store_id=selected_store
        )

        if not items:
            st.warning(
                "No items are available for this store."
            )
            return

        selected_item = st.selectbox(
            "Select Item",
            items,
            key="scenario_item",
        )

        with st.spinner(
            "Loading scenario data..."
        ):
            forecast_df = get_scenario_base_data(
                store_id=selected_store,
                item_id=selected_item,
            )

            historical_sales_df = (
                get_historical_sales_for_scenario(
                    store_id=selected_store,
                    item_id=selected_item,
                )
            )

        if forecast_df.empty:
            st.warning(
                "No forecast data is available for "
                "the selected item."
            )
            return

        base_price = get_latest_product_price(
            historical_sales_df,
            default_price=1.0,
        )

        st.caption(
            f"Current reference price: {base_price:,.2f}"
        )

        scenario_type = st.radio(
            "Select Scenario",
            [
                "Price Change",
                "Promotion",
            ],
            horizontal=True,
        )

        if scenario_type == "Price Change":
            scenario_df = render_price_scenario(
                forecast_df,
                base_price,
            )

        else:
            scenario_df = render_promotion_scenario(
                forecast_df
            )

        st.divider()

        render_inventory_impact(
            scenario_df
        )

        st.subheader(
            "Scenario Data"
        )

        st.dataframe(
            scenario_df,
            use_container_width=True,
            hide_index=True,
        )

        csv_data = scenario_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "Download Scenario Results",
            data=csv_data,
            file_name="scenario_results.csv",
            mime="text/csv",
            use_container_width=True,
        )

    except ValueError as exc:
        st.error(str(exc))

    except Exception as exc:
        st.error(
            "Unable to run scenario analysis."
        )

        with st.expander(
            "Technical Details"
        ):
            st.exception(exc)