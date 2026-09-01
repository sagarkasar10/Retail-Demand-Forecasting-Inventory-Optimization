"""
What-if scenario dashboard page.

Day 1 provides the scenario interface foundation.
The actual Week 3 LightGBM model integration can be connected
when the model artifact/loading mechanism is finalized.
"""

from __future__ import annotations
import streamlit as st
from src.dashboard.data_access import get_forecast_data


def render_scenarios() -> None:
    """
    Render the what-if scenario page.
    """
    st.title("What-if Scenarios")

    st.markdown(
        """
        Simulate changes in product price and compare the base
        forecast with a scenario forecast.
        """
    )

    col1, col2 = st.columns(2)

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

    price_change_pct = st.slider(
        "Price Change (%)",
        min_value=-50,
        max_value=50,
        value=0,
        step=5,
        help=(
            "Negative values represent price reductions. "
            "Positive values represent price increases."
        ),
    )

    st.caption(
        f"Selected scenario: {price_change_pct:+d}% price change"
    )

    if not store_id or not item_id:
        st.info(
            "Enter a Store ID and Item ID to load forecast data."
        )
        return

    if st.button(
        "Load Scenario Data",
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

            st.subheader("Base Forecast")

            base_demand = forecast_df[
                "predicted_demand"
            ].sum()

            st.metric(
                "Base Forecast Demand",
                f"{base_demand:,.0f}",
            )

            st.subheader("Scenario")

            st.info(
                "The Week 3 LightGBM model will be connected to "
                "this scenario interface. The modified price will "
                "then be passed through the trained model to calculate "
                "scenario demand."
            )

            if price_change_pct == 0:
                st.success(
                    "Base scenario selected: no price change."
                )
            else:
                st.write(
                    {
                        "Store": store_id,
                        "Item": item_id,
                        "Price Change": (
                            f"{price_change_pct:+d}%"
                        ),
                        "Base Forecast Demand": round(
                            float(base_demand),
                            2,
                        ),
                    }
                )

            st.subheader("Forecast Data")

            display_columns = [
                "forecast_date",
                "predicted_demand",
                "model_name",
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
                "Unable to load scenario data."
            )
            st.exception(exc)