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

    model = Prophet(
        yearly_seasonality=yearly_seasonality,
        weekly_seasonality=weekly_seasonality,
        daily_seasonality=daily_seasonality,
        interval_width=0.95,
    )

    return model


def add_event_regressors(
    model: Prophet,
    prophet_data: pd.DataFrame,
    regressor_columns: Optional[list] = None,
) -> Prophet:
    """
    Add optional numeric event regressors to Prophet.
    """

    regressor_columns = regressor_columns or []

    for column in regressor_columns:
        if column not in prophet_data.columns:
            raise ValueError(
                f"Regressor column '{column}' is missing."
            )

        model.add_regressor(column)

    return model


def train_prophet_model(
    prophet_data: pd.DataFrame,
    yearly_seasonality: bool = True,
    weekly_seasonality: bool = True,
    daily_seasonality: bool = False,
    regressor_columns: Optional[list] = None,
) -> Prophet:
    """
    Train Prophet using ds and y columns.
    """

    required_columns = {"ds", "y"}
    regressor_columns = regressor_columns or []

    required_columns.update(regressor_columns)

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
        )

        train_df[column] = train_df[column].fillna(0)

    train_df = (
        train_df
        .sort_values("ds")
        .reset_index(drop=True)
    )

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

    if len(train_df) < 2:
        raise ValueError(
            "Prophet requires at least two valid observations."
        )

    model = create_prophet_model(
        yearly_seasonality=yearly_seasonality,
        weekly_seasonality=weekly_seasonality,
        daily_seasonality=daily_seasonality,
    )

    model = add_event_regressors(
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

    forecast = forecast[
        [
            "ds",
            "yhat",
            "yhat_lower",
            "yhat_upper",
        ]
    ].tail(periods)

    forecast["yhat"] = forecast["yhat"].clip(lower=0)
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
    """
    Convert Prophet output into the standard forecast schema.
    """

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

    output = forecast.copy()

    output = output.rename(
        columns={
            "ds": "forecast_date",
            "yhat": "predicted_demand",
            "yhat_lower": "prediction_lower",
            "yhat_upper": "prediction_upper",
        }
    )

    output["item_id"] = item_id
    output["store_id"] = store_id
    output["dept_id"] = dept_id
    output["cat_id"] = cat_id
    output["model_name"] = model_name

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
        ]
    ]


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


def add_event_regressors(
    model: Prophet,
    prophet_data: pd.DataFrame,
    regressor_columns: Optional[list] = None,
) -> Prophet:
    """Add optional numeric regressors to Prophet."""

    regressor_columns = regressor_columns or []

    for column in regressor_columns:
        if column not in prophet_data.columns:
            raise ValueError(
                f"Regressor column '{column}' is missing."
            )

        model.add_regressor(column)

    return model


def prepare_prophet_training_data(
    prophet_data: pd.DataFrame,
    regressor_columns: Optional[list] = None,
) -> pd.DataFrame:
    """Clean and prepare Prophet training data."""

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
            "At least 30 observations are recommended "
            "for the Prophet training series."
        )

    return train_df


def train_prophet_model(
    prophet_data: pd.DataFrame,
    yearly_seasonality: bool = True,
    weekly_seasonality: bool = True,
    daily_seasonality: bool = False,
    regressor_columns: Optional[list] = None,
) -> Prophet:
    """Train a Prophet model."""

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

    model = add_event_regressors(
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
            "Forecast periods must be greater than zero."
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
    """Create the standard forecast output schema."""

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

    output = forecast.copy()

    output = output.rename(
        columns={
            "ds": "forecast_date",
            "yhat": "predicted_demand",
            "yhat_lower": "prediction_lower",
            "yhat_upper": "prediction_upper",
        }
    )

    output["item_id"] = item_id
    output["store_id"] = store_id
    output["dept_id"] = dept_id
    output["cat_id"] = cat_id
    output["model_name"] = model_name

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
        ]
    ]


def train_and_forecast_prophet(
    prophet_data: pd.DataFrame,
    periods: int = 30,
) -> pd.DataFrame:
    """Train Prophet and generate a future forecast."""

    model = train_prophet_model(
        prophet_data
    )

    return generate_prophet_forecast(
        model=model,
        periods=periods,
    )

