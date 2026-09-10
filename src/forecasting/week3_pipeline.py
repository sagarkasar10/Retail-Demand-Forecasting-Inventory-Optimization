from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pandas as pd

from src.forecasting.data_pipeline import (
    load_and_validate_forecasting_data,
    prepare_item_store_series,
    get_top_forecasting_series,
)
from src.forecasting.prophet_forecast import (
    run_prophet_forecast,
    validate_prophet_output,
)
from src.forecasting.lightgbm_forecast import (
    run_lightgbm_forecast,
    validate_lightgbm_output,
)
from src.forecasting.lightgbm_features import (
    prepare_lightgbm_features,
    get_lightgbm_feature_columns,
)
from src.forecasting.lightgbm_model import (
    train_lightgbm_model,
    predict_lightgbm,
)
from src.forecasting.model_comparison import (
    compare_prophet_and_lightgbm,
    validate_model_comparison,
    get_best_forecasting_model,
)
from src.forecasting.forecast_writer import (
    write_forecasts,
    write_metrics,
    write_model_run,
)


FORECAST_HORIZON = 30
TOP_SERIES = 5


def _evaluate_series_models(
    series: pd.DataFrame,
    item_id,
    store_id,
    evaluation_horizon: int = FORECAST_HORIZON,
) -> pd.DataFrame:
    """Evaluate Prophet and LightGBM on the same chronological holdout."""

    if len(series) <= evaluation_horizon + 28:
        raise ValueError(
            "Not enough history for a 30-day evaluation window "
            "and LightGBM lag/rolling features."
        )

    series = series.sort_values("date").reset_index(drop=True)

    train = series.iloc[:-evaluation_horizon].copy()
    test = series.iloc[-evaluation_horizon:].copy()

    # Prophet evaluation: train only on the historical portion.
    prophet_test = run_prophet_forecast(
        series=train,
        item_id=item_id,
        store_id=store_id,
        periods=evaluation_horizon,
    )
    validate_prophet_output(prophet_test)

    # LightGBM evaluation: build leakage-safe features from the full
    # series, but train only on rows before the holdout.
    featured = prepare_lightgbm_features(series)
    feature_columns = get_lightgbm_feature_columns(featured)

    train_features = featured[
        featured["date"] < test["date"].min()
    ].copy()
    test_features = featured[
        featured["date"] >= test["date"].min()
    ].copy()

    if train_features.empty or test_features.empty:
        raise ValueError("Unable to construct LightGBM evaluation split.")

    # Drop rows whose lag/rolling features cannot yet be calculated.
    train_features = train_features.dropna(
        subset=feature_columns + ["sales"]
    )
    test_features = test_features.dropna(
        subset=feature_columns + ["sales"]
    )

    if train_features.empty or test_features.empty:
        raise ValueError("LightGBM evaluation split contains no valid rows.")

    lgbm_model = train_lightgbm_model(
        train_features,
        feature_columns=feature_columns,
    )

    lightgbm_predictions = predict_lightgbm(
        lgbm_model,
        test_features,
        feature_columns=feature_columns,
    )

    # Align Prophet predictions and actual values by forecast date.
    actual_df = test[["date", "sales"]].copy()
    actual_df["date"] = pd.to_datetime(actual_df["date"])

    prophet_eval = prophet_test[
        ["forecast_date", "predicted_demand"]
    ].copy()
    prophet_eval["forecast_date"] = pd.to_datetime(
        prophet_eval["forecast_date"]
    )

    prophet_eval = prophet_eval.merge(
        actual_df,
        left_on="forecast_date",
        right_on="date",
        how="inner",
    )

    if prophet_eval.empty:
        raise ValueError("No overlapping dates for Prophet evaluation.")

    # LightGBM test rows already contain actual sales.
    lightgbm_eval = test_features[
        ["date", "sales"]
    ].copy()
    lightgbm_eval["predicted_demand"] = lightgbm_predictions.values

    comparison = compare_prophet_and_lightgbm(
        actual=prophet_eval["sales"].to_numpy(),
        prophet_predictions=prophet_eval["predicted_demand"].to_numpy(),
        lightgbm_predictions=lightgbm_eval["predicted_demand"].to_numpy(),
    )

    validate_model_comparison(comparison)

    return comparison


def run_week3_pipeline() -> dict:
    """Execute forecasting, evaluation, and model comparison for Week 3."""

    run_id = str(uuid.uuid4())
    start_time = datetime.now(timezone.utc)

    dataframe = load_and_validate_forecasting_data()

    series_keys = get_top_forecasting_series(
        dataframe,
        top_n=TOP_SERIES,
    )

    all_forecasts: list[pd.DataFrame] = []
    all_metrics: list[dict] = []
    comparisons: list[pd.DataFrame] = []

    for item_id, store_id in series_keys:
        series = prepare_item_store_series(
            dataframe=dataframe,
            item_id=item_id,
            store_id=store_id,
        )

        if len(series) < 30:
            continue

        # Generate both production forecasts from the complete history.
        prophet_forecast = run_prophet_forecast(
            series=series,
            item_id=item_id,
            store_id=store_id,
            periods=FORECAST_HORIZON,
        )
        validate_prophet_output(prophet_forecast)

        lightgbm_forecast = run_lightgbm_forecast(
            series=series,
            item_id=item_id,
            store_id=store_id,
            periods=FORECAST_HORIZON,
        )
        validate_lightgbm_output(lightgbm_forecast)

        all_forecasts.extend(
            [prophet_forecast, lightgbm_forecast]
        )

        # Compare both models using an unseen historical holdout.
        try:
            comparison = _evaluate_series_models(
                series=series,
                item_id=item_id,
                store_id=store_id,
                evaluation_horizon=FORECAST_HORIZON,
            )
        except ValueError:
            # A short series may be sufficient for forecasting but not
            # sufficient for the requested 30-day model evaluation.
            continue

        comparisons.append(comparison)

        for record in comparison.to_dict(orient="records"):
            record["item_id"] = item_id
            record["store_id"] = store_id
            all_metrics.append(record)

    if not all_forecasts:
        raise RuntimeError("No valid forecasts were generated.")

    forecast_dataframe = pd.concat(
        all_forecasts,
        ignore_index=True,
    )

    rows_written = write_forecasts(forecast_dataframe)

    comparison_dataframe = (
        pd.concat(comparisons, ignore_index=True)
        if comparisons
        else pd.DataFrame()
    )

    metrics_written = 0
    best_model = None

    if not comparison_dataframe.empty:
        # Aggregate model performance across evaluated series.
        aggregate_metrics = (
            comparison_dataframe
            .groupby("model_name", as_index=False)
            .agg(
                mae=("mae", "mean"),
                rmse=("rmse", "mean"),
                mape=("mape", "mean"),
                wape=("wape", "mean"),
                bias=("bias", "mean"),
                rows_evaluated=("rows_evaluated", "sum"),
            )
            .to_dict(orient="records")
        )

        best_model = get_best_forecasting_model(
            pd.DataFrame(aggregate_metrics)
        )

        metrics_written = write_metrics(
            aggregate_metrics
        )

    end_time = datetime.now(timezone.utc)

    write_model_run(
        run_id=run_id,
        model_name=best_model or "Prophet+LightGBM",
        run_type="week3_batch_forecast",
        status="SUCCESS",
        start_date=dataframe["date"].min(),
        end_date=dataframe["date"].max(),
        forecast_horizon=FORECAST_HORIZON,
    )

    return {
        "run_id": run_id,
        "model_name": best_model or "Prophet+LightGBM",
        "input_rows": len(dataframe),
        "series_processed": len(all_forecasts) // 2,
        "forecast_rows": len(forecast_dataframe),
        "rows_written": rows_written,
        "models_evaluated": (
            comparison_dataframe["model_name"]
            .nunique()
            if not comparison_dataframe.empty
            else 0
        ),
        "metrics_written": metrics_written,
        "best_model": best_model,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "status": "SUCCESS",
    }


def main() -> None:
    """Run the Week 3 forecasting workflow."""

    try:
        result = run_week3_pipeline()

        print("\nWeek 3 forecasting pipeline completed.")

        for key, value in result.items():
            print(f"{key}: {value}")

    except Exception as exc:
        print("\nWeek 3 forecasting pipeline failed.")
        print(f"Error: {exc}")
        raise


if __name__ == "__main__":
    main()
