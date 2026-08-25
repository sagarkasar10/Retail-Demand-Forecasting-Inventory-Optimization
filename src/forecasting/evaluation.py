import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error


def calculate_mae(
    actual,
    predicted,
) -> float:
    """Calculate Mean Absolute Error."""

    actual_array = np.asarray(actual, dtype=float)
    predicted_array = np.asarray(predicted, dtype=float)

    if len(actual_array) != len(predicted_array):
        raise ValueError(
            "Actual and predicted values must have the same length."
        )

    return float(
        mean_absolute_error(
            actual_array,
            predicted_array,
        )
    )


def calculate_rmse(
    actual,
    predicted,
) -> float:
    """Calculate Root Mean Squared Error."""

    actual_array = np.asarray(actual, dtype=float)
    predicted_array = np.asarray(predicted, dtype=float)

    if len(actual_array) != len(predicted_array):
        raise ValueError(
            "Actual and predicted values must have the same length."
        )

    mse = mean_squared_error(
        actual_array,
        predicted_array,
    )

    return float(np.sqrt(mse))


def calculate_mape(
    actual,
    predicted,
) -> float:
    """
    Calculate MAPE while excluding zero actual values.
    Returns percentage.
    """

    actual_array = np.asarray(
        actual,
        dtype=float,
    )

    predicted_array = np.asarray(
        predicted,
        dtype=float,
    )

    if len(actual_array) != len(predicted_array):
        raise ValueError(
            "Actual and predicted values must have the same length."
        )

    non_zero_mask = actual_array != 0

    if not np.any(non_zero_mask):
        return 0.0

    actual_non_zero = actual_array[
        non_zero_mask
    ]

    predicted_non_zero = predicted_array[
        non_zero_mask
    ]

    mape = np.mean(
        np.abs(
            (
                actual_non_zero
                - predicted_non_zero
            )
            / actual_non_zero
        )
    )

    return float(mape * 100)


def calculate_wape(
    actual,
    predicted,
) -> float:
    """
    Calculate Weighted Absolute Percentage Error.
    Returns percentage.
    """

    actual_array = np.asarray(
        actual,
        dtype=float,
    )

    predicted_array = np.asarray(
        predicted,
        dtype=float,
    )

    if len(actual_array) != len(predicted_array):
        raise ValueError(
            "Actual and predicted values must have the same length."
        )

    denominator = np.sum(
        np.abs(actual_array)
    )

    if denominator == 0:
        return 0.0

    numerator = np.sum(
        np.abs(
            actual_array - predicted_array
        )
    )

    return float(
        (numerator / denominator) * 100
    )


def evaluate_forecast(
    actual,
    predicted,
) -> dict:
    """Calculate all forecasting metrics."""

    actual_array = np.asarray(
        actual,
        dtype=float,
    )

    predicted_array = np.asarray(
        predicted,
        dtype=float,
    )

    if len(actual_array) != len(predicted_array):
        raise ValueError(
            "Actual and predicted values must have the same length."
        )

    if len(actual_array) == 0:
        raise ValueError(
            "Cannot evaluate an empty forecast."
        )

    return {
        "mae": calculate_mae(
            actual_array,
            predicted_array,
        ),
        "rmse": calculate_rmse(
            actual_array,
            predicted_array,
        ),
        "mape": calculate_mape(
            actual_array,
            predicted_array,
        ),
        "wape": calculate_wape(
            actual_array,
            predicted_array,
        ),
    }


def evaluate_forecast_dataframe(
    dataframe: pd.DataFrame,
    actual_column: str = "actual_demand",
    predicted_column: str = "predicted_demand",
) -> dict:
    """Evaluate predictions stored in a dataframe."""

    required_columns = {
        actual_column,
        predicted_column,
    }

    missing_columns = required_columns - set(
        dataframe.columns
    )

    if missing_columns:
        raise ValueError(
            f"Missing evaluation columns: "
            f"{sorted(missing_columns)}"
        )

    evaluation_df = dataframe[
        [actual_column, predicted_column]
    ].dropna()

    if evaluation_df.empty:
        raise ValueError(
            "No valid rows available for evaluation."
        )

    return evaluate_forecast(
        evaluation_df[actual_column],
        evaluation_df[predicted_column],
    )


def compare_models(
    prophet_metrics: dict,
    lightgbm_metrics: dict,
) -> pd.DataFrame:
    """Create a comparison table for Prophet and LightGBM."""

    rows = [
        {
            "model_name": "Prophet",
            **prophet_metrics,
        },
        {
            "model_name": "LightGBM",
            **lightgbm_metrics,
        },
    ]

    return pd.DataFrame(rows)