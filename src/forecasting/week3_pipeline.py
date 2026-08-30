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

from src.forecasting.forecast_writer import (
    write_forecasts,
    write_model_run,
)


FORECAST_HORIZON = 30
TOP_SERIES = 5


def run_week3_pipeline() -> dict:
    """Execute the complete Week 3 forecasting pipeline."""

    run_id = str(uuid.uuid4())

    start_time = datetime.now(
        timezone.utc
    )

    dataframe = load_and_validate_forecasting_data()

    series_keys = get_top_forecasting_series(
        dataframe,
        top_n=TOP_SERIES,
    )

    all_forecasts = []

    for item_id, store_id in series_keys:
        series = prepare_item_store_series(
            dataframe=dataframe,
            item_id=item_id,
            store_id=store_id,
        )

        if len(series) < 30:
            continue

        forecast = run_prophet_forecast(
            series=series,
            item_id=item_id,
            store_id=store_id,
            periods=FORECAST_HORIZON,
        )

        validate_prophet_output(
            forecast
        )

        all_forecasts.append(
            forecast
        )

    if not all_forecasts:
        raise RuntimeError(
            "No valid forecasts were generated."
        )

    forecast_dataframe = pd.concat(
        all_forecasts,
        ignore_index=True,
    )

    rows_written = write_forecasts(
        forecast_dataframe
    )

    end_time = datetime.now(
        timezone.utc
    )

    write_model_run(
        run_id=run_id,
        model_name="Prophet",
        run_type="week3_batch_forecast",
        status="SUCCESS",
        start_date=dataframe["date"].min(),
        end_date=dataframe["date"].max(),
        forecast_horizon=FORECAST_HORIZON,
    )

    return {
        "run_id": run_id,
        "model_name": "Prophet",
        "input_rows": len(dataframe),
        "series_processed": len(all_forecasts),
        "forecast_rows": len(forecast_dataframe),
        "rows_written": rows_written,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "status": "SUCCESS",
    }


def main() -> None:
    """Run the Week 3 forecasting workflow."""

    try:
        result = run_week3_pipeline()

        print(
            "\nWeek 3 forecasting pipeline completed."
        )

        for key, value in result.items():
            print(f"{key}: {value}")

    except Exception as exc:
        print(
            "\nWeek 3 forecasting pipeline failed."
        )

        print(
            f"Error: {exc}"
        )

        raise


if __name__ == "__main__":
    main()
