import pandas as pd


BASE_COLUMNS = [
    "date",
    "item_id",
    "store_id",
    "sales",
]

DEFAULT_LAGS = [1, 7, 14, 28]
DEFAULT_ROLLING_WINDOWS = [7, 14, 28]


def validate_lightgbm_input(dataframe: pd.DataFrame) -> None:
    """Validate the base dataset required for LightGBM."""

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
        raise ValueError(
            "LightGBM input contains null dates."
        )

    if dataframe["sales"].isna().any():
        raise ValueError(
            "LightGBM input contains null sales."
        )

    if (dataframe["sales"] < 0).any():
        raise ValueError(
            "LightGBM input contains negative sales."
        )


def create_calendar_features(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Create calendar features."""

    validate_lightgbm_input(dataframe)

    df = dataframe.copy()

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
    )

    if df["date"].isna().any():
        raise ValueError(
            "Invalid dates found in LightGBM input."
        )

    df["day_of_week"] = df["date"].dt.dayofweek
    df["day_of_month"] = df["date"].dt.day
    df["week_of_year"] = (
        df["date"].dt.isocalendar().week.astype(int)
    )
    df["month_number"] = df["date"].dt.month
    df["year_number"] = df["date"].dt.year

    return df


def create_lag_features(
    dataframe: pd.DataFrame,
    lags=None,
) -> pd.DataFrame:
    """
    Create historical sales lag features.

    Lag values are calculated independently for each
    item-store combination.
    """

    validate_lightgbm_input(dataframe)

    lags = lags or DEFAULT_LAGS

    df = dataframe.copy()

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
    )

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
    Create leakage-safe rolling demand features.

    The shift(1) ensures that the current day's sales
    are not used to calculate the current day's features.
    """

    validate_lightgbm_input(dataframe)

    windows = windows or DEFAULT_ROLLING_WINDOWS

    df = dataframe.copy()

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
    )

    df = df.sort_values(
        ["item_id", "store_id", "date"]
    ).reset_index(drop=True)

    for window in windows:
        if window <= 0:
            raise ValueError(
                "Rolling window values must be greater than zero."
            )

        df[f"rolling_mean_{window}"] = (
            df.groupby(
                ["item_id", "store_id"],
                sort=False,
            )["sales"]
            .transform(
                lambda series: (
                    series
                    .shift(1)
                    .rolling(
                        window=window,
                        min_periods=window,
                    )
                    .mean()
                )
            )
        )

    return df


def create_price_features(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create price-related features when sell_price
    is available.
    """

    df = dataframe.copy()

    if "sell_price" not in df.columns:
        return df

    df["sell_price"] = pd.to_numeric(
        df["sell_price"],
        errors="coerce",
    )

    df = df.sort_values(
        ["item_id", "store_id", "date"]
    ).reset_index(drop=True)

    df["price_change"] = (
        df.groupby(
            ["item_id", "store_id"],
            sort=False,
        )["sell_price"]
        .pct_change()
        .replace(
            [float("inf"), float("-inf")],
            0,
        )
        .fillna(0)
    )

    return df


def create_event_features(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create numeric event features when event columns
    are available.
    """

    df = dataframe.copy()

    if "event" in df.columns:
        df["has_event"] = (
            df["event"]
            .fillna("")
            .astype(str)
            .str.strip()
            .ne("")
            .astype(int)
        )

    if "event_type" in df.columns:
        df["has_event_type"] = (
            df["event_type"]
            .fillna("")
            .astype(str)
            .str.strip()
            .ne("")
            .astype(int)
        )

    return df


def prepare_lightgbm_features(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare the complete LightGBM feature dataset.

    Features include:
    - Calendar features
    - Historical lag features
    - Leakage-safe rolling features
    - Price features
    - Event indicators
    """

    df = create_calendar_features(
        dataframe
    )

    df = create_lag_features(
        df
    )

    df = create_rolling_features(
        df
    )

    df = create_price_features(
        df
    )

    df = create_event_features(
        df
    )

    return df


def get_lightgbm_feature_columns(
    dataframe: pd.DataFrame,
) -> list[str]:
    """
    Return the available numeric LightGBM feature columns.
    """

    base_features = [
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

    optional_features = [
        "sell_price",
        "price_change",
        "has_event",
        "has_event_type",
    ]

    return [
        column
        for column in base_features + optional_features
        if column in dataframe.columns
    ]