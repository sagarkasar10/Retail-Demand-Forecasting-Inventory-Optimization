import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error


def _validate_metric_inputs(
    actual,
    predicted,
) -> tuple[np.ndarray, np.ndarray]:
    """Validate and convert metric inputs."""

    actual_array = np.asarray(
        actual,
        dtype=float,
    )

    predicted_array = np.asarray(
        predicted,
        dtype=float,
    )

    if actual_array.ndim != 1 or predicted_array.ndim != 1:
        raise ValueError(
            "Actual and predicted values must be one-dimensional."
        )

    if len(actual_array) != len(predicted_array):
        raise ValueError(
            "Actual and predicted values must have the same length."
        )

    if len(actual_array) == 0:
        raise ValueError(
            "Cannot evaluate an empty forecast."
        )

    if not np.isfinite(actual_array).all():
        raise ValueError(
            "Actual values contain NaN or infinite values."
        )

    if not np.isfinite(predicted_array).all():
        raise ValueError(
            "Predicted values contain NaN or infinite values."
        )

    return actual_array, predicted_array


def calculate_mae(
    actual,
    predicted,
) -> float:
    """Calculate Mean Absolute Error."""

    actual_array, predicted_array = _validate_metric_inputs(
        actual,
        predicted,
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

    actual_array, predicted_array = _validate_metric_inputs(
        actual,
        predicted,
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

    Returns:
        MAPE as a percentage.
    """

    actual_array, predicted_array = _validate_metric_inputs(
        actual,
        predicted,
    )

    non_zero_mask = actual_array != 0

    if not np.any(non_zero_mask):
        return 0.0

    actual_non_zero = actual_array[non_zero_mask]
    predicted_non_zero = predicted_array[non_zero_mask]

    return float(
        np.mean(
            np.abs(
                (
                    actual_non_zero - predicted_non_zero
                )
                / actual_non_zero
            )
        )
        * 100
    )


def calculate_wape(
    actual,
    predicted,
) -> float:
    """Calculate Weighted Absolute Percentage Error."""

    actual_array, predicted_array = _validate_metric_inputs(
        actual,
        predicted,
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
    """Calculate all supported forecasting metrics."""

    actual_array, predicted_array = _validate_metric_inputs(
        actual,
        predicted,
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
    """Evaluate predictions contained in a dataframe."""

    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError(
            "dataframe must be a pandas DataFrame."
        )

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


def create_evaluation_dataframe(
    actual,
    predicted,
    model_name: str,
) -> pd.DataFrame:
    """Create row-level actual versus predicted data."""

    actual_array, predicted_array = _validate_metric_inputs(
        actual,
        predicted,
    )

    if not isinstance(model_name, str) or not model_name.strip():
        raise ValueError(
            "model_name is required."
        )

    return pd.DataFrame(
        {
            "actual_demand": actual_array,
            "predicted_demand": predicted_array,
            "model_name": model_name,
        }
    )