from typing import Optional

import pandas as pd
from prophet import Prophet


def create_prophet_model(
    yearly_seasonality: bool = True,
    weekly_seasonality: bool = True,
    daily_seasonality: bool = False,
) -> Prophet:
    """
    Create and configure a Prophet model.
    """

    return Prophet(
        yearly_seasonality=yearly_seasonality,
        weekly_seasonality=weekly_seasonality,
        daily_seasonality=daily_seasonality,
    )


def train_prophet_model(
    prophet_data: pd.DataFrame,
    yearly_seasonality: bool = True,
    weekly_seasonality: bool = True,
    daily_seasonality: bool = False,
) -> Prophet:
    """
    Train Prophet using a dataframe containing ds and y.
    """

    required_columns = {"ds", "y"}

    missing_columns = required_columns - set(
        prophet_data.columns
    )

    if missing_columns:
        raise ValueError(
            f"Missing Prophet columns: "
            f"{sorted(missing_columns)}"
        )

    if prophet_data.empty:
        raise ValueError(
            "Prophet training data cannot be empty."
        )

    train_df = prophet_data[
        ["ds", "y"]
    ].copy()

    train_df["ds"] = pd.to_datetime(
        train_df["ds"],
        errors="coerce",
    )

    train_df["y"] = pd.to_numeric(
        train_df["y"],
        errors="coerce",
    )

    train_df = train_df.dropna(
        subset=["ds", "y"]
    )

    train_df = train_df[
        train_df["y"] >= 0
    ]

    train_df = (
        train_df
        .groupby("ds", as_index=False)["y"]
        .sum()
        .sort_values("ds")
        .reset_index(drop=True)
    )

    if len(train_df) < 2:
        raise ValueError(
            "Prophet requires at least two valid observations."
        )

    model = create_prophet_model(
        yearly_seasonality=yearly_seasonality,
        weekly_seasonality=weekly_seasonality,
        daily_seasonality=daily_seasonality,
    )

    model.fit(train_df)

    return model


def generate_prophet_forecast(
    model: Prophet,
    periods: int = 30,
    frequency: str = "D",
) -> pd.DataFrame:
    """
    Generate future Prophet predictions.
    """

    if periods <= 0:
        raise ValueError(
            "Forecast periods must be greater than zero."
        )

    future = model.make_future_dataframe(
        periods=periods,
        freq=frequency,
    )

    forecast = model.predict(future)

    return forecast[
        [
            "ds",
            "yhat",
            "yhat_lower",
            "yhat_upper",
        ]
    ].tail(periods).reset_index(drop=True)


def train_and_forecast_prophet(
    prophet_data: pd.DataFrame,
    periods: int = 30,
) -> pd.DataFrame:
    """
    Train Prophet and generate a future forecast.
    """

    model = train_prophet_model(
        prophet_data
    )

    return generate_prophet_forecast(
        model=model,
        periods=periods,
    )