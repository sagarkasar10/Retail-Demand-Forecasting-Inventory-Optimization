import pandas as pd


BASE_COLUMNS = [
    "date",
    "item_id",
    "store_id",
    "sales",
]


def validate_lightgbm_input(dataframe: pd.DataFrame) -> None:
    """
    Validate the base dataset required for LightGBM feature engineering.
    """

    missing_columns = set(BASE_COLUMNS) - set(dataframe.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    if dataframe.empty:
        raise ValueError(
            "LightGBM input dataframe cannot be empty."
        )

    if dataframe["date"].isna().any():
        raise ValueError("LightGBM input contains null dates.")

    if dataframe["sales"].isna().any():
        raise ValueError("LightGBM input contains null sales.")

    if (dataframe["sales"] < 0).any():
        raise ValueError(
            "LightGBM input contains negative sales."
        )


def create_calendar_features(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create basic calendar features for the LightGBM pipeline.
    """

    validate_lightgbm_input(dataframe)

    df = dataframe.copy()

    df["date"] = pd.to_datetime(df["date"])

    df["day_of_week"] = df["date"].dt.dayofweek
    df["day_of_month"] = df["date"].dt.day
    df["week_of_year"] = df["date"].dt.isocalendar().week.astype(int)
    df["month_number"] = df["date"].dt.month
    df["year_number"] = df["date"].dt.year

    return df


def create_lag_features(
    dataframe: pd.DataFrame,
    lags=None,
) -> pd.DataFrame:
    """
    Create historical sales lag features.

    Features are calculated independently for each
    item-store combination.
    """

    validate_lightgbm_input(dataframe)

    lags = lags or [1, 7, 14, 28]

    df = dataframe.copy()

    df["date"] = pd.to_datetime(df["date"])

    df = df.sort_values(
        ["item_id", "store_id", "date"]
    ).reset_index(drop=True)

    grouped_sales = df.groupby(
        ["item_id", "store_id"],
        sort=False,
    )["sales"]

    for lag in lags:
        if lag <= 0:
            raise ValueError(
                "Lag values must be greater than zero."
            )

        df[f"lag_{lag}"] = grouped_sales.shift(lag)

    return df


def create_rolling_features(
    dataframe: pd.DataFrame,
    windows=None,
) -> pd.DataFrame:
    """
    Create historical rolling-demand features.

    Rolling calculations are shifted by one day so that
    today's target is never used to calculate today's feature.
    """

    validate_lightgbm_input(dataframe)

    windows = windows or [7, 14, 28]

    df = dataframe.copy()

    df["date"] = pd.to_datetime(df["date"])

    df = df.sort_values(
        ["item_id", "store_id", "date"]
    ).reset_index(drop=True)

    grouped_sales = df.groupby(
        ["item_id", "store_id"],
        sort=False,
    )["sales"]

    for window in windows:
        if window <= 0:
            raise ValueError(
                "Rolling window values must be greater than zero."
            )

        df[f"rolling_mean_{window}"] = (
            grouped_sales
            .shift(1)
            .rolling(window=window)
            .mean()
            .reset_index(level=[0, 1], drop=True)
        )

    return df


def prepare_lightgbm_features(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare the initial LightGBM feature dataset.
    """

    df = create_calendar_features(dataframe)

    df = create_lag_features(df)

    df = create_rolling_features(df)

    return df