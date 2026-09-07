"""
Reusable KPI components for the Streamlit dashboard.
"""

from __future__ import annotations

from typing import Optional

import streamlit as st


def show_kpi(
    title: str,
    value: str,
    delta: Optional[str] = None,
) -> None:
    """
    Display a single KPI.
    """
    st.metric(
        label=title,
        value=value,
        delta=delta,
    )


def show_kpi_row(
    metrics: list[dict],
) -> None:
    """
    Display multiple KPIs in one row.

    Each metric dictionary should contain:

        title
        value

    Optional:

        delta
    """
    columns = st.columns(len(metrics))

    for column, metric in zip(columns, metrics):
        with column:
            show_kpi(
                title=metric["title"],
                value=metric["value"],
                delta=metric.get("delta"),
            )
