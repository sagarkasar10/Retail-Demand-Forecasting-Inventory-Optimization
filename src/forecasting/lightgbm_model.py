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

OPTIONAL_FEATURES = [
    "sell_price",
    "price_change",
]


def create_lightgbm_model(
    n_estimators: int = 300,
    learning_rate: float = 0.05,
    max_depth: int = 8,
    num_leaves: int = 31,
    min_child_samples: int = 20,
    subsample: float = 0.8,
    colsample_bytree: float = 0.8,
    random_state: int = 42,
) -> LGBMRegressor:
    """Create a LightGBM regression model."""

    if n_estimators <= 0:
        raise ValueError(
            "n_estimators must be greater than zero."
        )

    if learning_rate <= 0:
        raise ValueError(
            "learning_rate must be greater than zero."
        )

    if num_leaves <= 1:
        raise ValueError(
            "num_leaves must be greater than one."
        )

    if not 0 < subsample <= 1:
        raise ValueError(
            "subsample must be between 0 and 1."
        )

    if not 0 < colsample_bytree <= 1:
        raise ValueError(
            "colsample_bytree must be between 0 and 1."
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


def get_available_features(
    dataframe: pd.DataFrame,
    feature_columns: Optional[list] = None,
) -> list:
    """Return requested features that exist in the dataframe."""

    features = feature_columns or DEFAULT_FEATURES

    missing_columns = set(features) - set(
        dataframe.columns
    )

    if missing_columns:
        raise ValueError(
            f"Missing LightGBM features: "
            f"{sorted(missing_columns)}"
        )

    return features


def prepare_training_data(
    dataframe: pd.DataFrame,
    feature_columns: Optional[list] = None,
):
    """Prepare X and y for LightGBM training."""

    features = get_available_features(
        dataframe,
        feature_columns,
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
            "No valid rows available for LightGBM training."
        )

    X = training_df[features]
    y = training_df["sales"]

    return X, y


def train_lightgbm_model(
    dataframe: pd.DataFrame,
    feature_columns: Optional[list] = None,
) -> LGBMRegressor:
    """Train a LightGBM regression model."""

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
    """Generate LightGBM predictions."""

    features = get_available_features(
        dataframe,
        feature_columns,
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


def get_feature_importance(
    model: LGBMRegressor,
    feature_columns: Optional[list] = None,
) -> pd.DataFrame:
    """Return LightGBM feature importance."""

    features = feature_columns or DEFAULT_FEATURES

    if len(features) != len(model.feature_importances_):
        raise ValueError(
            "Number of feature names does not match "
            "the trained model."
        )

    importance = pd.DataFrame(
        {
            "feature": features,
            "importance": model.feature_importances_,
        }
    )

    return importance.sort_values(
        "importance",
        ascending=False,
    ).reset_index(drop=True)
