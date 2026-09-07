
"""
Streamlit dashboard pages package.

This package contains the individual pages used by
the Retail Demand Forecasting & Inventory Optimization
Streamlit application.
"""

from dashboard.pages.forecast import render_forecast
from dashboard.pages.inventory import render_inventory
from dashboard.pages.model_performance import render_model_performance
from dashboard.pages.overview import render_overview
from dashboard.pages.scenarios import render_scenarios


_all_ = [
    "render_forecast",
    "render_inventory",
    "render_model_performance",
    "render_overview",
    "render_scenarios",
]