from typing import Optional

import pandas as pd
from prophet import Prophet


def create_prophet_model(
    yearly_seasonality: bool = True,
    weekly_seasonality: bool = True,
    daily_seasonality: bool = False,
    changepoint_prior_scale: float = 0.05,
    seasonality_prior_scale: float = 10.0,
) -> Prophet:
    """Create and configure a Prophet model."""

    if changepoint_prior_scale <= 0:
        raise ValueError(
            "changepoint_prior_scale must be greater than zero."
        )

    if seasonality_prior_scale <= 0:
        raise ValueError(
            "seasonality_prior_scale must be greater than zero."
        )

    return Prophet(
        yearly_seasonality=yearly_seasonality,
        weekly_seasonality=weekly_seasonality,
        daily_seasonality=daily_seasonality,
        changepoint_prior_scale=changepoint_prior_scale,
        seasonality_prior_scale=seasonality_prior_scale,
        interval_width=0.95,
    )


def prepare_prophet_training_data(
    prophet_data: pd.DataFrame,
    regressor_columns: Optional[list[str]] = None,
) -> pd.DataFrame:
    """Prepare data in Prophet ds/y format."""

    regressor_columns = regressor_columns or []

    required_columns = {
        "ds",
        "y",
        *regressor_columns,
    }

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

    train_df = prophet_data.copy()

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

    for column in regressor_columns:
        train_df[column] = pd.to_numeric(
            train_df[column],
            errors="coerce",
        ).fillna(0)

    train_df = train_df.sort_values(
        "ds"
    ).reset_index(drop=True)

    if train_df["ds"].duplicated().any():
        aggregation = {"y": "sum"}

        for column in regressor_columns:
            aggregation[column] = "mean"

        train_df = (
            train_df
            .groupby("ds", as_index=False)
            .agg(aggregation)
            .sort_values("ds")
            .reset_index(drop=True)
        )

    if len(train_df) < 30:
        raise ValueError(
            "At least 30 observations are required "
            "for Prophet training."
        )

    return train_df


def add_event_regressors(
    model: Prophet,
    train_df: pd.DataFrame,
    regressor_columns: Optional[list[str]] = None,
) -> Prophet:
    """Add numeric external regressors to Prophet."""

    regressor_columns = regressor_columns or []

    for column in regressor_columns:
        if column not in train_df.columns:
            raise ValueError(
                f"Regressor '{column}' is missing."
            )

        model.add_regressor(column)

    return model


def train_prophet_model(
    prophet_data: pd.DataFrame,
    yearly_seasonality: bool = True,
    weekly_seasonality: bool = True,
    daily_seasonality: bool = False,
    regressor_columns: Optional[list[str]] = None,
) -> Prophet:
    """Train the Prophet forecasting model."""

    regressor_columns = regressor_columns or []

    train_df = prepare_prophet_training_data(
        prophet_data,
        regressor_columns,
    )

    model = create_prophet_model(
        yearly_seasonality=yearly_seasonality,
        weekly_seasonality=weekly_seasonality,
        daily_seasonality=daily_seasonality,
    )

    add_event_regressors(
        model,
        train_df,
        regressor_columns,
    )

    model.fit(train_df)

    return model


def generate_prophet_forecast(
    model: Prophet,
    periods: int = 30,
    frequency: str = "D",
) -> pd.DataFrame:
    """Generate future Prophet predictions."""

    if periods <= 0:
        raise ValueError(
            "periods must be greater than zero."
        )

    future = model.make_future_dataframe(
        periods=periods,
        freq=frequency,
    )

    forecast = model.predict(future)

    forecast = forecast[
        [
            "ds",
            "yhat",
            "yhat_lower",
            "yhat_upper",
            "trend",
        ]
    ].tail(periods)

    forecast["yhat"] = forecast["yhat"].clip(
        lower=0
    )

    forecast["yhat_lower"] = forecast[
        "yhat_lower"
    ].clip(lower=0)

    forecast["yhat_upper"] = forecast[
        "yhat_upper"
    ].clip(lower=0)

    return forecast.reset_index(drop=True)


def create_prophet_forecast_output(
    forecast: pd.DataFrame,
    item_id=None,
    store_id=None,
    dept_id=None,
    cat_id=None,
    model_name: str = "Prophet",
) -> pd.DataFrame:
    """Create standardized Prophet forecast output."""

    required_columns = {
        "ds",
        "yhat",
        "yhat_lower",
        "yhat_upper",
    }

    missing_columns = required_columns - set(
        forecast.columns
    )

    if missing_columns:
        raise ValueError(
            f"Missing forecast columns: "
            f"{sorted(missing_columns)}"
        )

    output = forecast.rename(
        columns={
            "ds": "forecast_date",
            "yhat": "predicted_demand",
            "yhat_lower": "prediction_lower",
            "yhat_upper": "prediction_upper",
        }
    ).copy()

    output["item_id"] = item_id
    output["store_id"] = store_id
    output["dept_id"] = dept_id
    output["cat_id"] = cat_id
    output["model_name"] = model_name

    output["forecast_created_at"] = (
        pd.Timestamp.utcnow()
    )

    return output[
        [
            "forecast_date",
            "item_id",
            "store_id",
            "dept_id",
            "cat_id",
            "model_name",
            "predicted_demand",
            "prediction_lower",
            "prediction_upper",
            "forecast_created_at",
        ]
    ]


def train_and_forecast_prophet(
    prophet_data: pd.DataFrame,
    periods: int = 30,
    regressor_columns: Optional[list[str]] = None,
) -> pd.DataFrame:
    """Train Prophet and generate a future forecast."""

    model = train_prophet_model(
        prophet_data,
        regressor_columns=regressor_columns,
    )

    return generate_prophet_forecast(
        model=model,
        periods=periods,
    )