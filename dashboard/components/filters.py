"""
Reusable dashboard filter components.
"""

from __future__ import annotations

from typing import Optional

import streamlit as st


def select_filter(
    label: str,
    options: list[str],
    key: str,
    default: Optional[str] = None,
) -> Optional[str]:
    """
    Render a reusable select-box filter.
    """
    normalized_options = [
        str(option)
        for option in options
        if option is not None
    ]

    values = ["All"] + normalized_options

    default_index = 0

    if default is not None and default in values:
        default_index = values.index(default)

    selected = st.selectbox(
        label,
        values,
        index=default_index,
        key=key,
    )

    if selected == "All":
        return None

    return selected


def render_forecast_filters(
    stores: list[str],
    departments: list[str],
    categories: list[str],
    items: list[str],
) -> dict:
    """
    Render the common forecast filters.
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        store_id = select_filter(
            "Store",
            stores,
            "filter_store",
        )

    with col2:
        dept_id = select_filter(
            "Department",
            departments,
            "filter_department",
        )

    with col3:
        cat_id = select_filter(
            "Category",
            categories,
            "filter_category",
        )

    with col4:
        item_id = select_filter(
            "Item",
            items,
            "filter_item",
        )

    return {
        "store_id": store_id,
        "dept_id": dept_id,
        "cat_id": cat_id,
        "item_id": item_id,
    }