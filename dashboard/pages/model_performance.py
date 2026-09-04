import streamlit as st

from src.dashboard.data_access import (
    get_available_models,
    get_forecast_metrics,
    get_model_runs,
)


def render_model_performance():
    st.title("Model Performance")

    st.write(
        "Compare forecasting models using historical "
        "evaluation metrics and model execution records."
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

            st.dataframe(
                metrics_df,
                use_container_width=True,
                hide_index=True,
            )

            if "mae" in metrics_df.columns:
                best_mae = metrics_df.loc[
                    metrics_df["mae"].idxmin()
                ]

                st.metric(
                    "Best Model by MAE",
                    str(best_mae["model_name"]),
                    f"MAE: {best_mae['mae']:.4f}",
                )

            if "rmse" in metrics_df.columns:
                best_rmse = metrics_df.loc[
                    metrics_df["rmse"].idxmin()
                ]

                st.metric(
                    "Best Model by RMSE",
                    str(best_rmse["model_name"]),
                    f"RMSE: {best_rmse['rmse']:.4f}",
                )

            if "model_name" in metrics_df.columns:
                chart_df = (
                    metrics_df[
                        ["model_name", "mae", "rmse"]
                    ]
                    .set_index("model_name")
                )

                st.subheader(
                    "Model Error Comparison"
                )

                st.bar_chart(
                    chart_df
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
        else:
            if model_filter:
                runs_df = runs_df[
                    runs_df["model_name"].astype(str)
                    == model_filter
                ]

            st.dataframe(
                runs_df,
                use_container_width=True,
                hide_index=True,
            )

    except Exception as exc:
        st.error(
            "Unable to load model performance information."
        )

        with st.expander("Technical details"):
            st.exception(exc)