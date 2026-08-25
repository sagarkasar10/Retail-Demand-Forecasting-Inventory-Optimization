from typing import Optional

import pandas as pd
from lightgbm import LGBMRegressor


DEFAULT_FEATURES = [
    "day_of_week",
    "day_of_month",
    "week_of_year",
    "month_number",
    "year_number",
    "lag_1",
    "lag_7",
    "lag_14",
    "lag_28",
    "rolling_mean_7",
    "rolling_mean_14",
    "rolling_mean_28",
]


def create_lightgbm_model(
    n_estimators: int = 300,
    learning_rate: float = 0.05,
    max_depth: int = 8,
    num_leaves: int = 31,
    random_state: int = 42,
) -> LGBMRegressor:
    """
    Create a LightGBM regression model.
    """

    return LGBMRegressor(
        objective="regression",
        n_estimators=n_estimators,
        learning_rate=learning_rate,
        max_depth=max_depth,
        num_leaves=num_leaves,
        random_state=random_state,
        verbosity=-1,
    )


def prepare_training_data(
    dataframe: pd.DataFrame,
    feature_columns: Optional[list] = None,
):
    """
    Prepare X and y for LightGBM training.
    """

    features = feature_columns or DEFAULT_FEATURES

    missing_columns = set(features) - set(
        dataframe.columns
    )

    if missing_columns:
        raise ValueError(
            f"Missing LightGBM features: "
            f"{sorted(missing_columns)}"
        )

    if "sales" not in dataframe.columns:
        raise ValueError(
            "Training dataframe must contain sales."
        )

    training_df = dataframe[
        features + ["sales"]
    ].copy()

    training_df = training_df.dropna(
        subset=features + ["sales"]
    )

    if training_df.empty:
        raise ValueError(
            "No valid rows available for LightGBM training."
        )

    X = training_df[features]
    y = training_df["sales"]

    return X, y


def train_lightgbm_model(
    dataframe: pd.DataFrame,
    feature_columns: Optional[list] = None,
) -> LGBMRegressor:
    """
    Train a LightGBM regression model.
    """

    X, y = prepare_training_data(
        dataframe,
        feature_columns=feature_columns,
    )

    model = create_lightgbm_model()

    model.fit(X, y)

    return model


def predict_lightgbm(
    model: LGBMRegressor,
    dataframe: pd.DataFrame,
    feature_columns: Optional[list] = None,
) -> pd.Series:
    """
    Generate LightGBM predictions.
    """

    features = feature_columns or DEFAULT_FEATURES

    missing_columns = set(features) - set(
        dataframe.columns
    )

    if missing_columns:
        raise ValueError(
            f"Missing LightGBM features: "
            f"{sorted(missing_columns)}"
        )

    X = dataframe[features].copy()

    X = X.replace(
        [float("inf"), float("-inf")],
        pd.NA,
    )

    if X.isna().any().any():
        raise ValueError(
            "Prediction data contains missing or invalid features."
        )

    predictions = model.predict(X)

    return pd.Series(
        predictions,
        index=dataframe.index,
        name="predicted_demand",
    ).clip(lower=0)