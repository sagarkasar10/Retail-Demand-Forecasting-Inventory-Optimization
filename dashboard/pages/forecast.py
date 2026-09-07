import streamlit as st
import pandas as pd

from src.dashboard.data_access import (
    get_available_stores,
    get_available_departments,
    get_available_categories,
    get_available_items,
    get_available_models,
    get_forecast_data,
    get_forecast_date_range,
)


def _format_number(value: float) -> str:
    """Format dashboard numeric values."""
    return f"{value:,.2f}"


def render_forecast():
    st.title("Demand Forecast")

    st.write(
        "Analyze predicted demand across stores, categories, "
        "items, and forecasting models."
    )

    try:
        min_date, max_date = get_forecast_date_range()

        if min_date is None or max_date is None:
            st.warning(
                "No forecast data is available."
            )
            return

        stores = get_available_stores()
        departments = get_available_departments()
        categories = get_available_categories()
        models = get_available_models()

        col1, col2, col3 = st.columns(3)

        with col1:
            selected_store = st.selectbox(
                "Store",
                ["All"] + stores,
                key="forecast_store"
            )

        with col2:
            selected_department = st.selectbox(
                "Department",
                ["All"] + departments,
                key="forecast_department"
            )

        with col3:
            selected_category = st.selectbox(
                "Category",
                ["All"] + categories,
                key="forecast_category"
            )

        store_filter = (
            None
            if selected_store == "All"
            else selected_store
        )

        department_filter = (
            None
            if selected_department == "All"
            else selected_department
        )

        category_filter = (
            None
            if selected_category == "All"
            else selected_category
        )

        items = get_available_items(
            store_id=store_filter,
            dept_id=department_filter,
            cat_id=category_filter,
        )

        col4, col5 = st.columns(2)

        with col4:
            selected_item = st.selectbox(
                "Item",
                ["All"] + items,
                key="forecast_item"
            )

        with col5:
            selected_model = st.selectbox(
                "Forecast Model",
                ["All"] + models,
                key="forecast_model"
            )

        date_range = st.date_input(
            "Forecast Date Range",
            value=(
                min_date,
                max_date
            ),
            min_value=min_date,
            max_value=max_date,
            key="forecast_dates",
        )

        if len(date_range) != 2:
            st.info(
                "Select both a start date and end date."
            )
            return

        start_date, end_date = date_range

        if start_date > end_date:
            st.error(
                "Start date cannot be after end date."
            )
            return

        item_filter = (
            None
            if selected_item == "All"
            else selected_item
        )

        model_filter = (
            None
            if selected_model == "All"
            else selected_model
        )

        if st.button(
            "Load Forecast",
            type="primary",
            use_container_width=True,
        ):
            with st.spinner(
                "Loading forecast data..."
            ):
                forecast_df = get_forecast_data(
                    store_id=store_filter,
                    dept_id=department_filter,
                    cat_id=category_filter,
                    item_id=item_filter,
                    model_name=model_filter,
                    start_date=str(start_date),
                    end_date=str(end_date),
                )

            if forecast_df.empty:
                st.warning(
                    "No forecast records match the "
                    "selected filters."
                )
                return

            forecast_df["forecast_date"] = pd.to_datetime(
                forecast_df["forecast_date"]
            )

            forecast_df["predicted_demand"] = pd.to_numeric(
                forecast_df["predicted_demand"],
                errors="coerce"
            ).fillna(0)

            total_demand = float(
                forecast_df["predicted_demand"].sum()
            )

            average_demand = float(
                forecast_df["predicted_demand"].mean()
            )

            forecast_days = int(
                forecast_df[
                    "forecast_date"
                ].nunique()
            )

            max_demand = float(
                forecast_df["predicted_demand"].max()
            )

            st.subheader(
                "Forecast Summary"
            )

            kpi1, kpi2, kpi3, kpi4 = st.columns(4)

            kpi1.metric(
                "Total Demand",
                _format_number(total_demand)
            )

            kpi2.metric(
                "Average Demand",
                _format_number(average_demand)
            )

            kpi3.metric(
                "Forecast Days",
                f"{forecast_days:,}"
            )

            kpi4.metric(
                "Peak Demand",
                _format_number(max_demand)
            )

            st.divider()

            chart_df = (
                forecast_df
                .groupby(
                    "forecast_date",
                    as_index=False
                )["predicted_demand"]
                .sum()
                .sort_values("forecast_date")
                .set_index("forecast_date")
            )

            st.subheader(
                "Daily Predicted Demand"
            )

            st.line_chart(
                chart_df["predicted_demand"]
            )

            if (
                "actual_demand" in forecast_df.columns
                and
                forecast_df["actual_demand"].notna().any()
            ):
                comparison_df = forecast_df[
                    [
                        "forecast_date",
                        "predicted_demand",
                        "actual_demand",
                    ]
                ].copy()

                comparison_df["actual_demand"] = pd.to_numeric(
                    comparison_df["actual_demand"],
                    errors="coerce"
                )

                comparison_df = (
                    comparison_df
                    .groupby(
                        "forecast_date",
                        as_index=False
                    )
                    [
                        [
                            "predicted_demand",
                            "actual_demand",
                        ]
                    ]
                    .sum()
                    .set_index("forecast_date")
                )

                st.subheader(
                    "Predicted vs Actual Demand"
                )

                st.line_chart(
                    comparison_df
                )

            st.subheader(
                "Forecast Details"
            )

            display_columns = [
                "forecast_date",
                "store_id",
                "item_id",
                "dept_id",
                "cat_id",
                "model_name",
                "predicted_demand",
                "actual_demand",
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

            csv_data = forecast_df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                "Download Forecast CSV",
                data=csv_data,
                file_name="demand_forecast.csv",
                mime="text/csv",
                use_container_width=True,
            )

    except Exception as exc:
        st.error(
            "Unable to load forecast information."
        )

        with st.expander(
            "Technical details"
        ):
            st.exception(exc)
