from __future__ import annotations

import pandas as pd


def create_lightgbm_forecast_output(
    dataframe: pd.DataFrame,
    predictions,
    model_name: str = "LightGBM",
) -> pd.DataFrame:
    """Create the standard forecast output dataframe."""

    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError(
            "dataframe must be a pandas DataFrame."
        )

    if "date" not in dataframe.columns:
        raise ValueError(
            "Missing forecast columns: ['date']"
        )

    if len(predictions) != len(dataframe):
        raise ValueError(
            "Prediction length does not match dataframe length."
        )

    prediction_series = pd.Series(
        predictions,
        index=dataframe.index,
        dtype="float64",
    ).clip(lower=0)

    output_columns = {
        "forecast_date": dataframe["date"],
        "predicted_demand": prediction_series,
    }

    optional_columns = [
        "item_id",
        "store_id",
        "dept_id",
        "cat_id",
        "state_id",
    ]

    for column in optional_columns:
        if column in dataframe.columns:
            output_columns[column] = dataframe[column]

    output = pd.DataFrame(output_columns)

    output["model_name"] = model_name
    output["forecast_created_at"] = pd.Timestamp.now(
        tz="UTC"
    )

    return output


def aggregate_forecast_by_store(
    forecast_df: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate predicted demand at store-date level."""

    required_columns = {
        "forecast_date",
        "store_id",
        "predicted_demand",
    }

    missing_columns = required_columns - set(
        forecast_df.columns
    )

    if missing_columns:
        raise ValueError(
            f"Missing store aggregation columns: "
            f"{sorted(missing_columns)}"
        )

    return (
        forecast_df
        .groupby(
            [
                "forecast_date",
                "store_id",
            ],
            as_index=False,
        )["predicted_demand"]
        .sum()
        .sort_values(
            [
                "forecast_date",
                "store_id",
            ]
        )
        .reset_index(drop=True)
    )


def aggregate_forecast_by_department(
    forecast_df: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate predicted demand at department-date level."""

    required_columns = {
        "forecast_date",
        "dept_id",
        "predicted_demand",
    }

    missing_columns = required_columns - set(
        forecast_df.columns
    )

    if missing_columns:
        raise ValueError(
            f"Missing department aggregation columns: "
            f"{sorted(missing_columns)}"
        )

    return (
        forecast_df
        .groupby(
            [
                "forecast_date",
                "dept_id",
            ],
            as_index=False,
        )["predicted_demand"]
        .sum()
        .sort_values(
            [
                "forecast_date",
                "dept_id",
            ]
        )
        .reset_index(drop=True)
    )


def calculate_forecast_summary(
    forecast_df: pd.DataFrame,
) -> dict:
    """Calculate summary statistics for forecast output."""

    if forecast_df.empty:
        raise ValueError(
            "Forecast dataframe cannot be empty."
        )

    if "predicted_demand" not in forecast_df.columns:
        raise ValueError(
            "Forecast dataframe must contain predicted_demand."
        )

    predictions = pd.to_numeric(
        forecast_df["predicted_demand"],
        errors="coerce",
    ).dropna()

    if predictions.empty:
        raise ValueError(
            "No valid predicted demand values found."
        )

    return {
        "forecast_rows": int(len(predictions)),
        "total_predicted_demand": float(
            predictions.sum()
        ),
        "average_daily_demand": float(
            predictions.mean()
        ),
        "minimum_predicted_demand": float(
            predictions.min()
        ),
        "maximum_predicted_demand": float(
            predictions.max()
        ),
    }


def validate_forecast_output(
    forecast_df: pd.DataFrame,
) -> None:
    """Validate generated forecast records."""

    required_columns = {
        "forecast_date",
        "predicted_demand",
        "model_name",
    }

    missing_columns = required_columns - set(
        forecast_df.columns
    )

    if missing_columns:
        raise ValueError(
            f"Forecast output is missing: "
            f"{sorted(missing_columns)}"
        )

    if forecast_df.empty:
        raise ValueError(
            "Forecast output cannot be empty."
        )

    parsed_dates = pd.to_datetime(
        forecast_df["forecast_date"],
        errors="coerce",
    )

    if parsed_dates.isna().any():
        raise ValueError(
            "Forecast output contains invalid dates."
        )

    numeric_predictions = pd.to_numeric(
        forecast_df["predicted_demand"],
        errors="coerce",
    )

    if numeric_predictions.isna().any():
        raise ValueError(
            "Forecast output contains null or "
            "non-numeric predictions."
        )

    if (numeric_predictions < 0).any():
        raise ValueError(
            "Forecast output contains negative predictions."
        )

    if forecast_df["model_name"].isna().any():
        raise ValueError(
            "Forecast output contains null model names."
        )
    