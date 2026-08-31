from __future__ import annotations

from typing import Optional

import pandas as pd
from lightgbm import LGBMRegressor


DEFAULT_FEATURES = [
    "day_of_week",
    "day_of_month",
    "day_of_year",
    "week_of_year",
    "month_number",
    "quarter",
    "year_number",
    "is_weekend",
    "lag_1",
    "lag_7",
    "lag_14",
    "lag_28",
    "rolling_mean_7",
    "rolling_mean_14",
    "rolling_mean_28",
    "rolling_std_7",
    "rolling_std_14",
    "rolling_std_28",
    "sell_price",
    "price_change",
    "price_change_7d",
    "has_event",
    "has_event_type",
]


def create_lightgbm_model(
    n_estimators: int = 500,
    learning_rate: float = 0.03,
    max_depth: int = 8,
    num_leaves: int = 31,
    min_child_samples: int = 20,
    subsample: float = 0.8,
    colsample_bytree: float = 0.8,
    random_state: int = 42,
) -> LGBMRegressor:
    """Create a LightGBM demand forecasting model."""

    if n_estimators <= 0:
        raise ValueError(
            "n_estimators must be greater than zero."
        )

    if learning_rate <= 0:
        raise ValueError(
            "learning_rate must be greater than zero."
        )

    if max_depth == 0 or max_depth < -1:
        raise ValueError(
            "max_depth must be -1 or greater than zero."
        )

    if num_leaves <= 1:
        raise ValueError(
            "num_leaves must be greater than one."
        )

    return LGBMRegressor(
        objective="regression",
        n_estimators=n_estimators,
        learning_rate=learning_rate,
        max_depth=max_depth,
        num_leaves=num_leaves,
        min_child_samples=min_child_samples,
        subsample=subsample,
        colsample_bytree=colsample_bytree,
        random_state=random_state,
        verbosity=-1,
    )


def prepare_training_data(
    dataframe: pd.DataFrame,
    feature_columns: Optional[list[str]] = None,
):
    """Prepare LightGBM training data."""

    features = feature_columns or DEFAULT_FEATURES

    missing_features = set(features) - set(
        dataframe.columns
    )

    if missing_features:
        raise ValueError(
            f"Missing LightGBM features: "
            f"{sorted(missing_features)}"
        )

    if "sales" not in dataframe.columns:
        raise ValueError(
            "Training dataframe must contain sales."
        )

    training_df = dataframe[
        features + ["sales"]
    ].copy()

    training_df = training_df.replace(
        [float("inf"), float("-inf")],
        pd.NA,
    )

    training_df = training_df.dropna(
        subset=features + ["sales"]
    )

    if training_df.empty:
        raise ValueError(
            "No valid rows available for training."
        )

    return (
        training_df[features].astype(float),
        training_df["sales"].astype(float),
    )


def train_lightgbm_model(
    dataframe: pd.DataFrame,
    feature_columns: Optional[list[str]] = None,
    model_params: Optional[dict] = None,
) -> LGBMRegressor:
    """Train a LightGBM model."""

    X, y = prepare_training_data(
        dataframe,
        feature_columns,
    )

    model = create_lightgbm_model(
        **(model_params or {})
    )

    model.fit(X, y)

    return model


def predict_lightgbm(
    model: LGBMRegressor,
    dataframe: pd.DataFrame,
    feature_columns: Optional[list[str]] = None,
) -> pd.Series:
    """Generate LightGBM predictions."""

    features = feature_columns or DEFAULT_FEATURES

    missing_features = set(features) - set(
        dataframe.columns
    )

    if missing_features:
        raise ValueError(
            f"Missing prediction features: "
            f"{sorted(missing_features)}"
        )

    X = dataframe[features].copy()

    X = X.replace(
        [float("inf"), float("-inf")],
        pd.NA,
    )

    if X.isna().any().any():
        raise ValueError(
            "Prediction data contains missing features."
        )

    predictions = model.predict(
        X.astype(float)
    )

    return pd.Series(
        predictions,
        index=dataframe.index,
        name="predicted_demand",
    ).clip(lower=0)


def recursive_forecast(
    model: LGBMRegressor,
    historical_data: pd.DataFrame,
    future_features: pd.DataFrame,
    feature_columns: list[str],
) -> pd.DataFrame:
    """
    Generate forecasts from a prepared future feature dataset.

    Future features must already contain the required lag and
    rolling features. This method is intended for production
    inference after feature preparation.
    """

    if historical_data.empty:
        raise ValueError(
            "Historical data cannot be empty."
        )

    if future_features.empty:
        raise ValueError(
            "Future features cannot be empty."
        )

    missing_features = set(feature_columns) - set(
        future_features.columns
    )

    if missing_features:
        raise ValueError(
            f"Missing future features: "
            f"{sorted(missing_features)}"
        )

    predictions = predict_lightgbm(
        model,
        future_features,
        feature_columns,
    )

    output = future_features[
        [
            column
            for column in [
                "date",
                "item_id",
                "store_id",
                "dept_id",
                "cat_id",
                "state_id",
            ]
            if column in future_features.columns
        ]
    ].copy()

    output["predicted_demand"] = predictions.values

    return output.reset_index(drop=True)


def get_feature_importance(
    model: LGBMRegressor,
    feature_columns: Optional[list[str]] = None,
) -> pd.DataFrame:
    """Return feature importance."""

    features = feature_columns or DEFAULT_FEATURES

    if len(features) != len(
        model.feature_importances_
    ):
        raise ValueError(
            "Feature names do not match the trained model."
        )

    return (
        pd.DataFrame(
            {
                "feature": features,
                "importance": model.feature_importances_,
            }
        )
        .sort_values(
            "importance",
            ascending=False,
        )
        .reset_index(drop=True)
    )


def get_model_parameters(
    model: LGBMRegressor,
) -> dict:
    """Return model parameters."""

    return model.get_params()