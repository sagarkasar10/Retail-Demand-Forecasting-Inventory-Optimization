import pandas as pd
import streamlit as st


def render_demand_line_chart(
    df: pd.DataFrame,
    date_column: str = "forecast_date",
    value_column: str = "predicted_demand",
    title: str = "Demand Forecast",
):
    """
    Render a demand line chart.
    """
    if df.empty:
        st.info("No chart data available.")
        return

    if date_column not in df.columns:
        st.error(
            f"Missing chart date column: {date_column}"
        )
        return

    if value_column not in df.columns:
        st.error(
            f"Missing chart value column: {value_column}"
        )
        return

    chart_df = df[
        [date_column, value_column]
    ].copy()

    chart_df[date_column] = pd.to_datetime(
        chart_df[date_column]
    )

    chart_df[value_column] = pd.to_numeric(
        chart_df[value_column],
        errors="coerce"
    ).fillna(0)

    chart_df = (
        chart_df
        .groupby(date_column, as_index=False)[value_column]
        .sum()
        .sort_values(date_column)
    )

    chart_df = chart_df.set_index(
        date_column
    )

    st.subheader(title)

    st.line_chart(
        chart_df[value_column]
    )


def render_base_vs_scenario_chart(
    df: pd.DataFrame,
):
    """
    Render base demand against scenario demand.
    """
    if df.empty:
        st.info("No scenario data available.")
        return

    required_columns = {
        "forecast_date",
        "base_demand",
        "scenario_demand",
    }

    missing_columns = (
        required_columns -
        set(df.columns)
    )

    if missing_columns:
        st.error(
            f"Missing scenario chart columns: {missing_columns}"
        )
        return

    chart_df = df[
        [
            "forecast_date",
            "base_demand",
            "scenario_demand",
        ]
    ].copy()

    chart_df["forecast_date"] = pd.to_datetime(
        chart_df["forecast_date"]
    )

    chart_df["base_demand"] = pd.to_numeric(
        chart_df["base_demand"],
        errors="coerce"
    ).fillna(0)

    chart_df["scenario_demand"] = pd.to_numeric(
        chart_df["scenario_demand"],
        errors="coerce"
    ).fillna(0)

    chart_df = (
        chart_df
        .groupby("forecast_date", as_index=False)
        [
            ["base_demand", "scenario_demand"]
        ]
        .sum()
        .sort_values("forecast_date")
    )

    chart_df = chart_df.set_index(
        "forecast_date"
    )

    st.subheader(
        "Base Demand vs Scenario Demand"
    )

    st.line_chart(
        chart_df[
            [
                "base_demand",
                "scenario_demand",
            ]
        ]
    )


def render_top_items_chart(
    df: pd.DataFrame,
    item_column: str = "item_id",
    demand_column: str = "predicted_demand",
    top_n: int = 10,
):
    """
    Render top items by predicted demand.
    """
    if df.empty:
        st.info("No item demand data available.")
        return

    required_columns = {
        item_column,
        demand_column,
    }

    missing_columns = (
        required_columns -
        set(df.columns)
    )

    if missing_columns:
        st.error(
            f"Missing item chart columns: {missing_columns}"
        )
        return

    chart_df = df[
        [item_column, demand_column]
    ].copy()

    chart_df[demand_column] = pd.to_numeric(
        chart_df[demand_column],
        errors="coerce"
    ).fillna(0)

    chart_df = (
        chart_df
        .groupby(item_column, as_index=False)[
            demand_column
        ]
        .sum()
        .sort_values(
            demand_column,
            ascending=False
        )
        .head(top_n)
    )

    chart_df = chart_df.set_index(
        item_column
    )

    st.subheader(
        f"Top {top_n} Items by Forecast Demand"
    )

    st.bar_chart(
        chart_df[demand_column]
    )
