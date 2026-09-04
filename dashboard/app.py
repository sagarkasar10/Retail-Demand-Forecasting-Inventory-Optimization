import streamlit as st

from dashboard.pages.forecast import render_forecast
from dashboard.pages.inventory import render_inventory
from dashboard.pages.overview import render_overview
from dashboard.pages.scenarios import render_scenarios
from dashboard.pages.model_performance import (
    render_model_performance
)


st.set_page_config(
    page_title="Retail Demand Forecasting",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    st.sidebar.title(
        "Retail Analytics"
    )

    st.sidebar.caption(
        "Demand Forecasting & Inventory Optimization"
    )

    page = st.sidebar.radio(
        "Navigation",
        [
            "Overview",
            "Demand Forecast",
            "Inventory",
            "What-if Scenarios",
            "Model Performance",
        ],
    )

    if page == "Overview":
        render_overview()

    elif page == "Demand Forecast":
        render_forecast()

    elif page == "Inventory":
        render_inventory()

    elif page == "What-if Scenarios":
        render_scenarios()

    elif page == "Model Performance":
        render_model_performance()


if __name__ == "__main__":
    main()
