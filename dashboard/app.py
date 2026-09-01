"""
Main Streamlit application for the Retail Demand Forecasting
and Inventory Optimization dashboard.
"""

import streamlit as st

from dashboard.pages.overview import render_overview


st.set_page_config(
    page_title="Retail Demand Forecasting",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


def render_sidebar() -> str:
    """
    Render the application sidebar and return the selected page.
    """
    st.sidebar.title("Retail Analytics")

    st.sidebar.markdown(
        """
        ### Retail Demand Forecasting
        Demand forecasting and inventory optimization platform.
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
        "Data source: BigQuery"
    )

    return page


def render_placeholder(title: str, description: str) -> None:
    """
    Render a temporary page until the responsible team member
    implements the complete page.
    """
    st.title(title)
    st.info(description)


def main() -> None:
    """
    Main Streamlit application flow.
    """
    page = render_sidebar()

    if page == "Overview":
        render_overview()

    elif page == "Demand Forecast":
        render_placeholder(
            "Demand Forecast",
            "The demand forecast page will be implemented next.",
        )

    elif page == "Inventory":
        render_placeholder(
            "Inventory",
            "The inventory analysis page will be implemented next.",
        )

    elif page == "What-if Scenarios":
        render_placeholder(
            "What-if Scenarios",
            "The scenario analysis page will be implemented next.",
        )

    elif page == "Model Performance":
        render_placeholder(
            "Model Performance",
            "The model performance page will be implemented next.",
        )


if __name__ == "__main__":
    main()
