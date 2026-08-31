from __future__ import annotations

import pandas as pd
from lightgbm import LGBMRegressor


DEFAULT_PARAMETER_GRID = [
    {
        "n_estimators": 300,
        "learning_rate": 0.05,
        "num_leaves": 31,
        "max_depth": 8,
        "min_child_samples": 20,
    },
    {
        "n_estimators": 500,
        "learning_rate": 0.03,
        "num_leaves": 31,
        "max_depth": 8,
        "min_child_samples": 20,
    },
    {
        "n_estimators": 500,
        "learning_rate": 0.03,
        "num_leaves": 63,
        "max_depth": 10,
        "min_child_samples": 20,
    },
    {
        "n_estimators": 700,
        "learning_rate": 0.02,
        "num_leaves": 63,
        "max_depth": 10,
        "min_child_samples": 30,
    },
]


def validate_training_data(
    train_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    feature_columns: list[str],
) -> None:
    """Validate train and validation datasets."""

    if train_df.empty:
        raise ValueError(
            "Training dataframe cannot be empty."
        )

    if validation_df.empty:
        raise ValueError(
            "Validation dataframe cannot be empty."
        )

    required = set(feature_columns) | {"sales"}

    missing_train = required - set(
        train_df.columns
    )

    missing_validation = required - set(
        validation_df.columns
    )

    if missing_train:
        raise ValueError(
            f"Training data is missing: "
            f"{sorted(missing_train)}"
        )

    if missing_validation:
        raise ValueError(
            f"Validation data is missing: "
            f"{sorted(missing_validation)}"
        )


def calculate_wape(
    actual,
    predicted,
) -> float:
    """Calculate WAPE as a percentage."""

    actual_series = pd.Series(
        actual,
        dtype="float64",
    )

    predicted_series = pd.Series(
        predicted,
        dtype="float64",
    )

    if len(actual_series) != len(
        predicted_series
    ):
        raise ValueError(
            "Actual and predicted values must have equal length."
        )

    denominator = actual_series.abs().sum()

    if denominator == 0:
        return 0.0

    numerator = (
        actual_series - predicted_series
    ).abs().sum()

    return float(
        numerator / denominator * 100
    )


def train_candidate_model(
    train_df: pd.DataFrame,
    feature_columns: list[str],
    parameters: dict,
) -> LGBMRegressor:
    """Train one LightGBM candidate."""

    X_train = train_df[
        feature_columns
    ].astype(float)

    y_train = train_df[
        "sales"
    ].astype(float)

    model = LGBMRegressor(
        objective="regression",
        random_state=42,
        subsample=0.8,
        colsample_bytree=0.8,
        verbosity=-1,
        **parameters,
    )

    model.fit(
        X_train,
        y_train,
    )

    return model


def tune_lightgbm(
    train_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    feature_columns: list[str],
    parameter_grid: list[dict] | None = None,
):
    """
    Select the best LightGBM configuration using
    chronological validation data and WAPE.
    """

    validate_training_data(
        train_df,
        validation_df,
        feature_columns,
    )

    parameter_grid = (
        parameter_grid
        or DEFAULT_PARAMETER_GRID
    )

    X_validation = validation_df[
        feature_columns
    ].astype(float)

    y_validation = validation_df[
        "sales"
    ].astype(float)

    results = []
    best_model = None
    best_wape = float("inf")

    for index, parameters in enumerate(
        parameter_grid,
        start=1,
    ):
        model = train_candidate_model(
            train_df,
            feature_columns,
            parameters,
        )

        predictions = model.predict(
            X_validation
        )

        predictions = pd.Series(
            predictions
        ).clip(lower=0)

        wape = calculate_wape(
            y_validation,
            predictions,
        )

        result = {
            "candidate": index,
            "wape": wape,
            **parameters,
        }

        results.append(result)

        if wape < best_wape:
            best_wape = wape
            best_model = model

    if best_model is None:
        raise RuntimeError(
            "LightGBM tuning did not produce a model."
        )

    results_df = pd.DataFrame(
        results
    ).sort_values(
        "wape"
    ).reset_index(drop=True)

    return best_model, results_df


def get_best_parameters(
    tuning_results: pd.DataFrame,
) -> dict:
    """Return the parameter configuration with the lowest WAPE."""

    if tuning_results.empty:
        raise ValueError(
            "Tuning results cannot be empty."
        )

    if "wape" not in tuning_results.columns:
        raise ValueError(
            "Tuning results must contain wape."
        )

    best_row = tuning_results.loc[
        tuning_results["wape"].idxmin()
    ]

    excluded_columns = {
        "candidate",
        "wape",
    }

    return {
        column: best_row[column]
        for column in tuning_results.columns
        if column not in excluded_columns
    }