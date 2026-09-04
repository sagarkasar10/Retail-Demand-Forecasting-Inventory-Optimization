import streamlit as st

from src.dashboard.data_access import (
    get_available_stores,
    get_available_items,
    get_forecast_data,
)

from src.dashboard.scenario_service import (
    apply_price_scenario,
    summarize_scenario,
)

from dashboard.components.charts import (
    render_base_vs_scenario_chart,
)


def render_scenarios():
    st.title("What-if Price Scenario")

    st.write(
        "Estimate how a price increase or decrease may affect "
        "future product demand."
    )

    try:
        stores = get_available_stores()

        if not stores:
            st.warning("No stores are available.")
            return

        selected_store = st.selectbox(
            "Store",
            stores,
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
            "Item",
            items,
        )

        price_change = st.slider(
            "Price Change (%)",
            min_value=-50.0,
            max_value=100.0,
            value=0.0,
            step=5.0,
        )

        elasticity = st.number_input(
            "Price Elasticity",
            min_value=-10.0,
            max_value=0.0,
            value=-1.0,
            step=0.1,
        )

        if st.button(
            "Run Scenario",
            type="primary",
            use_container_width=True,
        ):

            with st.spinner(
                "Loading forecast and calculating scenario..."
            ):
                forecast_df = get_forecast_data(
                    store_id=selected_store,
                    item_id=selected_item,
                )

            if forecast_df.empty:
                st.warning(
                    "No forecast data found for the selected item."
                )
                return

            scenario_df = apply_price_scenario(
                forecast_df=forecast_df,
                price_change_percent=price_change,
                elasticity=elasticity,
            )

            summary = summarize_scenario(
                scenario_df,
                price_change_percent=price_change,
            )

            st.subheader("Scenario Impact")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Base Demand",
                f"{summary['base_demand']:,.0f}",
            )

            col2.metric(
                "Scenario Demand",
                f"{summary['scenario_demand']:,.0f}",
            )

            col3.metric(
                "Demand Difference",
                f"{summary['demand_difference']:,.0f}",
            )

            col4.metric(
                "Revenue Change",
                f"{summary['revenue_difference_percent']:.2f}%",
            )

            if summary["demand_difference"] > 0:
                st.success(
                    "The selected price scenario is estimated "
                    "to increase demand."
                )

            elif summary["demand_difference"] < 0:
                st.warning(
                    "The selected price scenario is estimated "
                    "to decrease demand."
                )

            else:
                st.info(
                    "The selected price scenario does not "
                    "change estimated demand."
                )

            st.divider()

            render_base_vs_scenario_chart(
                scenario_df
            )

            st.subheader(
                "Scenario Details"
            )

            display_columns = [
                "forecast_date",
                "base_demand",
                "scenario_demand",
                "demand_difference",
                "demand_difference_percent",
            ]

            available_columns = [
                column
                for column in display_columns
                if column in scenario_df.columns
            ]

            st.dataframe(
                scenario_df[available_columns],
                use_container_width=True,
                hide_index=True,
            )

            csv_data = scenario_df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                "Download Scenario CSV",
                data=csv_data,
                file_name="price_scenario.csv",
                mime="text/csv",
                use_container_width=True,
            )

    except ValueError as exc:
        st.error(str(exc))

    except Exception as exc:
        st.error(
            "Unable to calculate the selected price scenario."
        )

        with st.expander("Technical details"):
            st.exception(exc)