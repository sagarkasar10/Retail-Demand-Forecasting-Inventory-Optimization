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
<<<<<<< HEAD
    """Validate the base dataset required for LightGBM."""
=======
    """Validate the base dataset required for LightGBM features."""
>>>>>>> shelly_mittal

    missing_columns = set(BASE_COLUMNS) - set(dataframe.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    if dataframe.empty:
<<<<<<< HEAD
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
=======
        raise ValueError("LightGBM input dataframe cannot be empty.")

    if dataframe["date"].isna().any():
        raise ValueError("LightGBM input contains invalid dates.")

    if dataframe["sales"].isna().any():
        raise ValueError("LightGBM input contains null sales values.")

    if (dataframe["sales"] < 0).any():
        raise ValueError("LightGBM input contains negative sales values.")
>>>>>>> shelly_mittal


def create_calendar_features(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
<<<<<<< HEAD
    """Create calendar features."""
=======
    """Create calendar-based forecasting features."""
>>>>>>> shelly_mittal

    validate_lightgbm_input(dataframe)

    df = dataframe.copy()

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
    )

<<<<<<< HEAD
    if df["date"].isna().any():
        raise ValueError(
            "Invalid dates found in LightGBM input."
        )

    df["day_of_week"] = df["date"].dt.dayofweek
    df["day_of_month"] = df["date"].dt.day
=======
    df["day_of_week"] = df["date"].dt.dayofweek
    df["day_of_month"] = df["date"].dt.day
    df["day_of_year"] = df["date"].dt.dayofyear
>>>>>>> shelly_mittal
    df["week_of_year"] = (
        df["date"].dt.isocalendar().week.astype(int)
    )
    df["month_number"] = df["date"].dt.month
<<<<<<< HEAD
    df["year_number"] = df["date"].dt.year
=======
    df["quarter"] = df["date"].dt.quarter
    df["year_number"] = df["date"].dt.year
    df["is_weekend"] = (
        df["day_of_week"] >= 5
    ).astype(int)
>>>>>>> shelly_mittal

    return df


def create_lag_features(
    dataframe: pd.DataFrame,
<<<<<<< HEAD
    lags=None,
) -> pd.DataFrame:
    """
    Create historical sales lag features.

    Lag values are calculated independently for each
    item-store combination.
    """
=======
    lags: list[int] | None = None,
) -> pd.DataFrame:
    """Create historical sales lag features."""
>>>>>>> shelly_mittal

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
<<<<<<< HEAD
    windows=None,
=======
    windows: list[int] | None = None,
>>>>>>> shelly_mittal
) -> pd.DataFrame:
    """
    Create leakage-safe rolling demand features.

<<<<<<< HEAD
    The shift(1) ensures that the current day's sales
    are not used to calculate the current day's features.
=======
    The one-day shift prevents the current day's sales
    from being included in its own rolling statistics.
>>>>>>> shelly_mittal
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

<<<<<<< HEAD
=======
    grouped = df.groupby(
        ["item_id", "store_id"],
        sort=False,
    )["sales"]

>>>>>>> shelly_mittal
    for window in windows:
        if window <= 0:
            raise ValueError(
                "Rolling window values must be greater than zero."
            )

<<<<<<< HEAD
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
=======
        shifted = grouped.shift(1)

        df[f"rolling_mean_{window}"] = (
            shifted.groupby(
                [
                    df["item_id"],
                    df["store_id"],
                ]
            )
            .rolling(
                window=window,
                min_periods=window,
            )
            .mean()
            .reset_index(
                level=[0, 1],
                drop=True,
            )
        )

        df[f"rolling_std_{window}"] = (
            shifted.groupby(
                [
                    df["item_id"],
                    df["store_id"],
                ]
            )
            .rolling(
                window=window,
                min_periods=window,
            )
            .std()
            .reset_index(
                level=[0, 1],
                drop=True,
>>>>>>> shelly_mittal
            )
        )

    return df


def create_price_features(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
<<<<<<< HEAD
    """
    Create price-related features when sell_price
    is available.
    """
=======
    """Create price and price-change features."""
>>>>>>> shelly_mittal

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

<<<<<<< HEAD
    df["price_change"] = (
        df.groupby(
            ["item_id", "store_id"],
            sort=False,
        )["sell_price"]
=======
    grouped_price = df.groupby(
        ["item_id", "store_id"],
        sort=False,
    )["sell_price"]

    df["price_change"] = (
        grouped_price
>>>>>>> shelly_mittal
        .pct_change()
        .replace(
            [float("inf"), float("-inf")],
            0,
        )
        .fillna(0)
    )

<<<<<<< HEAD
=======
    df["price_change_7d"] = (
        grouped_price
        .pct_change(periods=7)
        .replace(
            [float("inf"), float("-inf")],
            0,
        )
        .fillna(0)
    )

>>>>>>> shelly_mittal
    return df


def create_event_features(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
<<<<<<< HEAD
    """
    Create numeric event features when event columns
    are available.
    """
=======
    """Create event and promotion-related numeric features."""
>>>>>>> shelly_mittal

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
<<<<<<< HEAD
=======
    else:
        df["has_event"] = 0
>>>>>>> shelly_mittal

    if "event_type" in df.columns:
        df["has_event_type"] = (
            df["event_type"]
            .fillna("")
            .astype(str)
            .str.strip()
            .ne("")
            .astype(int)
        )
<<<<<<< HEAD
=======
    else:
        df["has_event_type"] = 0

    return df


def create_hierarchy_features(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Create numeric representations of retail hierarchy fields."""

    df = dataframe.copy()

    categorical_columns = [
        "item_id",
        "dept_id",
        "cat_id",
        "store_id",
        "state_id",
    ]

    for column in categorical_columns:
        if column in df.columns:
            df[f"{column}_code"] = (
                df[column]
                .astype("category")
                .cat.codes
            )
>>>>>>> shelly_mittal

    return df


def prepare_lightgbm_features(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
<<<<<<< HEAD
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
=======
    """Prepare the complete Day 5 LightGBM feature dataset."""

    df = create_calendar_features(dataframe)
    df = create_lag_features(df)
    df = create_rolling_features(df)
    df = create_price_features(df)
    df = create_event_features(df)
    df = create_hierarchy_features(df)
>>>>>>> shelly_mittal

    return df


<<<<<<< HEAD
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
=======
def get_feature_columns(
    dataframe: pd.DataFrame,
) -> list[str]:
    """Return numeric features suitable for LightGBM."""

    excluded_columns = {
        "date",
        "sales",
        "item_id",
        "dept_id",
        "cat_id",
        "store_id",
        "state_id",
        "event",
        "event_type",
    }

    features = [
        column
        for column in dataframe.columns
        if column not in excluded_columns
        and pd.api.types.is_numeric_dtype(
            dataframe[column]
        )
    ]

    if not features:
        raise ValueError(
            "No numeric LightGBM features were found."
        )

    return features
>>>>>>> shelly_mittal
