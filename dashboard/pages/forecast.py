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
from dashboard.components.charts import render_demand_line_chart


def render_forecast():
    st.title("Demand Forecast")

    st.write(
        "Explore forecasted product demand by store, department, "
        "category, item, and forecasting model."
    )

    try:
        min_date, max_date = get_forecast_date_range()

        if min_date is None or max_date is None:
            st.warning("No forecast data is currently available.")
            return

        stores = get_available_stores()
        departments = get_available_departments()
        categories = get_available_categories()
        models = get_available_models()

        col1, col2, col3 = st.columns(3)

        with col1:
            selected_store = st.selectbox(
                "Store",
                ["All"] + stores
            )

        with col2:
            selected_department = st.selectbox(
                "Department",
                ["All"] + departments
            )

        with col3:
            selected_category = st.selectbox(
                "Category",
                ["All"] + categories
            )

        store_filter = (
            None if selected_store == "All"
            else selected_store
        )

        department_filter = (
            None if selected_department == "All"
            else selected_department
        )

        category_filter = (
            None if selected_category == "All"
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
                ["All"] + items
            )

        with col5:
            selected_model = st.selectbox(
                "Forecast Model",
                ["All"] + models
            )

        selected_start, selected_end = st.date_input(
            "Forecast Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )

        if selected_start > selected_end:
            st.error("Start date cannot be after end date.")
            return

        item_filter = (
            None if selected_item == "All"
            else selected_item
        )

        model_filter = (
            None if selected_model == "All"
            else selected_model
        )

        if st.button(
            "Load Forecast",
            type="primary",
            use_container_width=True
        ):
            with st.spinner("Loading forecast data..."):
                forecast_df = get_forecast_data(
                    store_id=store_filter,
                    dept_id=department_filter,
                    cat_id=category_filter,
                    item_id=item_filter,
                    model_name=model_filter,
                    start_date=str(selected_start),
                    end_date=str(selected_end),
                )

            if forecast_df.empty:
                st.warning(
                    "No forecast records found for the selected filters."
                )
                return

            forecast_df["forecast_date"] = pd.to_datetime(
                forecast_df["forecast_date"]
            )

            total_demand = forecast_df[
                "predicted_demand"
            ].sum()

            average_daily_demand = forecast_df[
                "predicted_demand"
            ].mean()

            forecast_days = forecast_df[
                "forecast_date"
            ].nunique()

            st.subheader("Forecast Summary")

            kpi1, kpi2, kpi3 = st.columns(3)

            kpi1.metric(
                "Total Forecast Demand",
                f"{total_demand:,.0f}"
            )

            kpi2.metric(
                "Average Daily Demand",
                f"{average_daily_demand:,.2f}"
            )

            kpi3.metric(
                "Forecast Days",
                f"{forecast_days:,}"
            )

            st.divider()

            render_demand_line_chart(
                forecast_df,
                date_column="forecast_date",
                value_column="predicted_demand",
                title="Predicted Daily Demand",
            )

            st.subheader("Forecast Details")

            display_columns = [
                "forecast_date",
                "store_id",
                "item_id",
                "dept_id",
                "cat_id",
                "model_name",
                "predicted_demand",
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

        with st.expander("Technical details"):
            st.exception(exc)
