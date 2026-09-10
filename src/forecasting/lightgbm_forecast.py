from __future__ import annotations

import pandas as pd

from src.forecasting.lightgbm_features import (
    prepare_lightgbm_features,
    get_lightgbm_feature_columns,
)
from src.forecasting.lightgbm_model import (
    train_lightgbm_model,
    predict_lightgbm,
)


def run_lightgbm_training(
    dataframe: pd.DataFrame,
    feature_columns: list[str] | None = None,
):
    """Prepare features and train a LightGBM demand model."""

    if dataframe.empty:
        raise ValueError(
            "LightGBM training dataframe cannot be empty."
        )

    featured = prepare_lightgbm_features(dataframe)

    features = feature_columns or get_lightgbm_feature_columns(
        featured
    )

    training_data = featured.dropna(
        subset=features + ["sales"]
    ).copy()

    if training_data.empty:
        raise ValueError(
            "No valid rows are available for LightGBM training."
        )

    model = train_lightgbm_model(
        training_data,
        feature_columns=features,
    )

    return model, features


def run_lightgbm_prediction(
    model,
    dataframe: pd.DataFrame,
    feature_columns: list[str] | None = None,
) -> pd.DataFrame:
    """Generate LightGBM predictions for prepared feature data."""

    if dataframe.empty:
        raise ValueError(
            "Prediction dataframe cannot be empty."
        )

    featured = (
        dataframe
        if feature_columns
        else prepare_lightgbm_features(dataframe)
    )

    features = feature_columns or get_lightgbm_feature_columns(
        featured
    )

    output = featured.copy()
    predictions = predict_lightgbm(
        model,
        output,
        feature_columns=features,
    )

    output["predicted_demand"] = predictions.values
    output["model_name"] = "LightGBM"

    return output


def run_lightgbm_forecast(
    series: pd.DataFrame,
    item_id=None,
    store_id=None,
    dept_id=None,
    cat_id=None,
    periods: int = 30,
) -> pd.DataFrame:
    """
    Train LightGBM on the complete history and recursively forecast
    the requested number of future days.

    Recursive prediction updates the history with each predicted value,
    allowing future lag and rolling features to use prior predictions.
    """

    if series.empty:
        raise ValueError(
            "LightGBM input cannot be empty."
        )

    if periods <= 0:
        raise ValueError(
            "Forecast periods must be greater than zero."
        )

    history = series[
        ["date", "sales"]
    ].copy()

    history["date"] = pd.to_datetime(
        history["date"],
        errors="coerce",
    )
    history["sales"] = pd.to_numeric(
        history["sales"],
        errors="coerce",
    )

    history = (
        history
        .dropna(subset=["date", "sales"])
        .sort_values("date")
        .drop_duplicates("date", keep="last")
        .reset_index(drop=True)
    )

    if len(history) < 30:
        raise ValueError(
            "At least 30 observations are required for LightGBM forecasting."
        )

    training_features = prepare_lightgbm_features(history)

    feature_columns = get_lightgbm_feature_columns(
        training_features
    )

    training_data = training_features.dropna(
        subset=feature_columns + ["sales"]
    ).copy()

    if training_data.empty:
        raise ValueError(
            "No valid rows are available after LightGBM feature preparation."
        )

    model = train_lightgbm_model(
        training_data,
        feature_columns=feature_columns,
    )

    future_rows = []

    for _ in range(periods):
        next_date = history["date"].max() + pd.Timedelta(days=1)

        candidate = pd.concat(
            [
                history,
                pd.DataFrame(
                    {
                        "date": [next_date],
                        "sales": [history["sales"].iloc[-1]],
                    }
                ),
            ],
            ignore_index=True,
        )

        candidate_features = prepare_lightgbm_features(
            candidate
        )

        next_features = candidate_features.tail(1)

        # The final row's feature values depend only on history up to
        # the previous day because all lag/rolling features use shift(1).
        prediction = predict_lightgbm(
            model,
            next_features,
            feature_columns=feature_columns,
        ).iloc[0]

        prediction = max(float(prediction), 0.0)

        history = pd.concat(
            [
                history,
                pd.DataFrame(
                    {
                        "date": [next_date],
                        "sales": [prediction],
                    }
                ),
            ],
            ignore_index=True,
        )

        future_rows.append(
            {
                "forecast_date": next_date,
                "item_id": item_id,
                "store_id": store_id,
                "dept_id": dept_id,
                "cat_id": cat_id,
                "model_name": "LightGBM",
                "predicted_demand": prediction,
                "prediction_lower": None,
                "prediction_upper": None,
            }
        )

    return pd.DataFrame(future_rows)


def create_lightgbm_forecast_output(
    model,
    future_dataframe: pd.DataFrame,
    item_id=None,
    store_id=None,
    dept_id=None,
    cat_id=None,
    feature_columns: list[str] | None = None,
) -> pd.DataFrame:
    """Create standardized LightGBM forecast output."""

    if future_dataframe.empty:
        raise ValueError(
            "Future dataframe cannot be empty."
        )

    featured = (
        future_dataframe
        if feature_columns
        else prepare_lightgbm_features(future_dataframe)
    )

    features = feature_columns or get_lightgbm_feature_columns(
        featured
    )

    predictions = predict_lightgbm(
        model,
        featured,
        feature_columns=features,
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
            "forecast_created_at": pd.Timestamp.now(tz="UTC"),
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

    missing = required_columns - set(forecast.columns)

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

    if (forecast["predicted_demand"] < 0).any():
        raise ValueError(
            "LightGBM output contains negative predictions."
        )
