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
    """Validate the base dataset required for LightGBM features."""

    missing_columns = set(BASE_COLUMNS) - set(dataframe.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    if dataframe.empty:
        raise ValueError("LightGBM input dataframe cannot be empty.")

    if dataframe["date"].isna().any():
        raise ValueError("LightGBM input contains invalid dates.")

    if dataframe["sales"].isna().any():
        raise ValueError("LightGBM input contains null sales values.")

    if (dataframe["sales"] < 0).any():
        raise ValueError("LightGBM input contains negative sales values.")


def create_calendar_features(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Create calendar-based forecasting features."""

    validate_lightgbm_input(dataframe)

    df = dataframe.copy()

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
    )

    df["day_of_week"] = df["date"].dt.dayofweek
    df["day_of_month"] = df["date"].dt.day
    df["day_of_year"] = df["date"].dt.dayofyear
    df["week_of_year"] = (
        df["date"].dt.isocalendar().week.astype(int)
    )
    df["month_number"] = df["date"].dt.month
    df["quarter"] = df["date"].dt.quarter
    df["year_number"] = df["date"].dt.year
    df["is_weekend"] = (
        df["day_of_week"] >= 5
    ).astype(int)

    return df


def create_lag_features(
    dataframe: pd.DataFrame,
    lags: list[int] | None = None,
) -> pd.DataFrame:
    """Create historical sales lag features."""

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
    windows: list[int] | None = None,
) -> pd.DataFrame:
    """
    Create leakage-safe rolling demand features.

    The one-day shift prevents the current day's sales
    from being included in its own rolling statistics.
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

    grouped = df.groupby(
        ["item_id", "store_id"],
        sort=False,
    )["sales"]

    for window in windows:
        if window <= 0:
            raise ValueError(
                "Rolling window values must be greater than zero."
            )

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
            )
        )

    return df


def create_price_features(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Create price and price-change features."""

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

    grouped_price = df.groupby(
        ["item_id", "store_id"],
        sort=False,
    )["sell_price"]

    df["price_change"] = (
        grouped_price
        .pct_change()
        .replace(
            [float("inf"), float("-inf")],
            0,
        )
        .fillna(0)
    )

    df["price_change_7d"] = (
        grouped_price
        .pct_change(periods=7)
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
    """Create event and promotion-related numeric features."""

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
    else:
        df["has_event"] = 0

    if "event_type" in df.columns:
        df["has_event_type"] = (
            df["event_type"]
            .fillna("")
            .astype(str)
            .str.strip()
            .ne("")
            .astype(int)
        )
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

    return df


def prepare_lightgbm_features(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Prepare the complete Day 5 LightGBM feature dataset."""

    df = create_calendar_features(dataframe)
    df = create_lag_features(df)
    df = create_rolling_features(df)
    df = create_price_features(df)
    df = create_event_features(df)
    df = create_hierarchy_features(df)

    return df


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
