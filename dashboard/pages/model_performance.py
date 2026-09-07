import streamlit as st

from src.dashboard.data_access import (
    get_available_models,
    get_forecast_metrics,
    get_model_runs,
)

from dashboard.components.charts import (
    render_model_error_chart,
)


def render_model_performance():
    st.title("Model Performance")

    st.write(
        "Compare forecasting models using accuracy metrics "
        "and model execution history."
    )

    try:
        models = get_available_models()

        if not models:
            st.warning(
                "No forecasting models are available."
            )
            return

        selected_model = st.selectbox(
            "Model",
            ["All"] + models,
            key="performance_model"
        )

        model_filter = (
            None
            if selected_model == "All"
            else selected_model
        )

        metrics_df = get_forecast_metrics(
            model_name=model_filter
        )

        if metrics_df.empty:
            st.warning(
                "No model evaluation metrics are available."
            )
        else:
            st.subheader(
                "Forecast Accuracy Metrics"
            )

            metric_columns = [
                "model_name",
                "mae",
                "rmse",
                "mape",
                "r2_score",
                "evaluated_at",
            ]

            available_columns = [
                column
                for column in metric_columns
                if column in metrics_df.columns
            ]

            st.dataframe(
                metrics_df[available_columns],
                use_container_width=True,
                hide_index=True,
            )

            if "mae" in metrics_df.columns:
                valid_mae = metrics_df.dropna(
                    subset=["mae"]
                )

                if not valid_mae.empty:
                    best_mae = valid_mae.loc[
                        valid_mae["mae"].idxmin()
                    ]

                    st.metric(
                        "Best Model by MAE",
                        str(
                            best_mae["model_name"]
                        ),
                        f"MAE: {best_mae['mae']:.4f}",
                    )

            if "rmse" in metrics_df.columns:
                valid_rmse = metrics_df.dropna(
                    subset=["rmse"]
                )

                if not valid_rmse.empty:
                    best_rmse = valid_rmse.loc[
                        valid_rmse["rmse"].idxmin()
                    ]

                    st.metric(
                        "Best Model by RMSE",
                        str(
                            best_rmse["model_name"]
                        ),
                        f"RMSE: {best_rmse['rmse']:.4f}",
                    )

            render_model_error_chart(
                metrics_df
            )

        st.divider()

        st.subheader(
            "Model Execution History"
        )

        runs_df = get_model_runs()

        if runs_df.empty:
            st.info(
                "No model execution records are available."
            )
            return

        if model_filter:
            runs_df = runs_df[
                runs_df["model_name"].astype(str)
                == model_filter
            ]

        if runs_df.empty:
            st.info(
                "No execution records found for "
                "the selected model."
            )
            return

        st.dataframe(
            runs_df,
            use_container_width=True,
            hide_index=True,
        )

        completed_runs = runs_df[
            runs_df["status"].astype(str).str.lower()
            == "completed"
        ]

        failed_runs = runs_df[
            runs_df["status"].astype(str).str.lower()
            == "failed"
        ]

        col1, col2 = st.columns(2)

        col1.metric(
            "Completed Runs",
            len(completed_runs)
        )

        col2.metric(
            "Failed Runs",
            len(failed_runs)
        )

    except Exception as exc:
        st.error(
            "Unable to load model performance information."
        )

        with st.expander(
            "Technical details"
        ):
            st.exception(exc)