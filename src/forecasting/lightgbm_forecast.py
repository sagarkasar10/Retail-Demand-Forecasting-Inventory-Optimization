from __future__ import annotations

import pandas as pd

from src.forecasting.lightgbm_model import (
    DEFAULT_FEATURES,
    train_lightgbm_model,
    predict_lightgbm,
)


def run_lightgbm_training(
    dataframe: pd.DataFrame,
):
    """Train LightGBM using prepared historical features."""

    if dataframe.empty:
        raise ValueError(
            "LightGBM training dataframe cannot be empty."
        )

    training_data = dataframe.copy()

    model = train_lightgbm_model(
        training_data,
        feature_columns=DEFAULT_FEATURES,
    )

    return model


def run_lightgbm_prediction(
    model,
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Generate LightGBM predictions."""

    if dataframe.empty:
        raise ValueError(
            "Prediction dataframe cannot be empty."
        )

    output = dataframe.copy()

    output["predicted_demand"] = predict_lightgbm(
        model,
        output,
        feature_columns=DEFAULT_FEATURES,
    )

    output["model_name"] = "LightGBM"

    return output


def create_lightgbm_forecast_output(
    model,
    future_dataframe: pd.DataFrame,
    item_id=None,
    store_id=None,
    dept_id=None,
    cat_id=None,
) -> pd.DataFrame:
    """Create standardized LightGBM forecast output."""

    if future_dataframe.empty:
        raise ValueError(
            "Future dataframe cannot be empty."
        )

    predictions = predict_lightgbm(
        model,
        future_dataframe,
        feature_columns=DEFAULT_FEATURES,
    )

    output = pd.DataFrame(
        {
            "forecast_date": pd.to_datetime(
                future_dataframe["date"],
                errors="coerce",
            ),
            "item_id": item_id,
            "store_id": store_id,
            "dept_id": dept_id,
            "cat_id": cat_id,
            "model_name": "LightGBM",
            "predicted_demand": predictions.values,
            "prediction_lower": None,
            "prediction_upper": None,
            "forecast_created_at": pd.Timestamp.utcnow(),
        }
    )

    output["predicted_demand"] = output[
        "predicted_demand"
    ].clip(lower=0)

    return output


def validate_lightgbm_output(
    forecast: pd.DataFrame,
) -> None:
    """Validate LightGBM forecast output."""

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
            f"Missing LightGBM columns: {sorted(missing)}"
        )

    if forecast.empty:
        raise ValueError(
            "LightGBM forecast output is empty."
        )

    if forecast["forecast_date"].isna().any():
        raise ValueError(
            "LightGBM output contains invalid dates."
        )

    if forecast["predicted_demand"].isna().any():
        raise ValueError(
            "LightGBM output contains null predictions."
        )

    if (
        forecast["predicted_demand"] < 0
    ).any():
        raise ValueError(
            "LightGBM output contains negative predictions."
        )