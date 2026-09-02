"""
Main Streamlit application.
"""

import streamlit as st

from dashboard.pages.forecast import render_forecast
from dashboard.pages.inventory import render_inventory
from dashboard.pages.overview import render_overview
from dashboard.pages.scenarios import render_scenarios


st.set_page_config(
    page_title="Retail Demand Forecasting",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


def render_model_performance() -> None:
    """
    Temporary model-performance page.
    """
    st.title("Model Performance")

    st.info(
        "Model performance visualization will be implemented "
        "in the next dashboard iteration."
    )


def render_sidebar() -> str:
    """
    Render the application sidebar.
    """
    st.sidebar.title("Retail Analytics")

    st.sidebar.markdown(
        """
        **Retail Demand Forecasting & Inventory Optimization**

        Monitor demand, forecasts, inventory and scenarios.
        """
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

    st.sidebar.divider()

    st.sidebar.caption(
        "Powered by BigQuery + Streamlit"
    )

    return page


def main() -> None:
    """
    Main dashboard execution flow.
    """
    page = render_sidebar()                                                               

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
