from __future__ import annotations

import pandas as pd

from src.forecasting.prophet_model import (
    train_prophet_model,
    generate_prophet_forecast,
    create_prophet_forecast_output,
)


def run_prophet_forecast(
    series: pd.DataFrame,
    item_id,
    store_id,
    dept_id=None,
    cat_id=None,
    periods: int = 30,
) -> pd.DataFrame:
    """Train Prophet for one item-store series and forecast demand."""

    if series.empty:
        raise ValueError(
            "Prophet input cannot be empty."
        )

    if periods <= 0:
        raise ValueError(
            "Forecast periods must be greater than zero."
        )

    training_data = series[
        ["date", "sales"]
    ].copy()

    training_data = training_data.rename(
        columns={
            "date": "ds",
            "sales": "y",
        }
    )

    training_data["ds"] = pd.to_datetime(
        training_data["ds"],
        errors="coerce",
    )

    training_data["y"] = pd.to_numeric(
        training_data["y"],
        errors="coerce",
    )

    training_data = training_data.dropna(
        subset=["ds", "y"]
    )

    training_data["y"] = training_data[
        "y"
    ].clip(lower=0)

    model = train_prophet_model(
        training_data
    )

    forecast = generate_prophet_forecast(
        model,
        periods=periods,
    )

    return create_prophet_forecast_output(
        forecast=forecast,
        item_id=item_id,
        store_id=store_id,
        dept_id=dept_id,
        cat_id=cat_id,
        model_name="Prophet",
    )


def run_prophet_batch(
    series_list: list[dict],
    periods: int = 30,
) -> pd.DataFrame:
    """Run Prophet for multiple item-store series."""

    outputs = []

    for series_info in series_list:
        series = series_info["data"]

        forecast = run_prophet_forecast(
            series=series,
            item_id=series_info.get("item_id"),
            store_id=series_info.get("store_id"),
            dept_id=series_info.get("dept_id"),
            cat_id=series_info.get("cat_id"),
            periods=periods,
        )

        outputs.append(forecast)

    if not outputs:
        return pd.DataFrame()

    return pd.concat(
        outputs,
        ignore_index=True,
    )


def validate_prophet_output(
    forecast: pd.DataFrame,
) -> None:
    """Validate Prophet forecast output."""

    required_columns = {
        "forecast_date",
        "item_id",
        "store_id",
        "model_name",
        "predicted_demand",
    }

    missing = required_columns - set(
        forecast.columns
    )

    if missing:
        raise ValueError(
            f"Missing Prophet output columns: "
            f"{sorted(missing)}"
        )

    if forecast.empty:
        raise ValueError(
            "Prophet forecast output is empty."
        )

    if forecast["predicted_demand"].isna().any():
        raise ValueError(
            "Prophet output contains null predictions."
        )

    if (
        forecast["predicted_demand"] < 0
    ).any():
        raise ValueError(
            "Prophet output contains negative predictions."
        )