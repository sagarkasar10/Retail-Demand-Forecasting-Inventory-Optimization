
import pandas as pd

from src.forecasting.data_loader import (
    load_daily_sales,
    validate_daily_sales,
    get_top_item_store_series,
)


def load_and_validate_forecasting_data() -> pd.DataFrame:
    """Load the Week 2 daily sales mart and validate it."""

    dataframe = load_daily_sales()

    validate_daily_sales(dataframe)

    dataframe["date"] = pd.to_datetime(
        dataframe["date"],
        errors="coerce",
    )

    dataframe["sales"] = pd.to_numeric(
        dataframe["sales"],
        errors="coerce",
    )

    if "sell_price" in dataframe.columns:
        dataframe["sell_price"] = pd.to_numeric(
            dataframe["sell_price"],
            errors="coerce",
        )

    dataframe = dataframe.sort_values(
        ["date", "store_id", "item_id"]
    ).reset_index(drop=True)

    return dataframe


def prepare_item_store_series(
    dataframe: pd.DataFrame,
    item_id,
    store_id,
) -> pd.DataFrame:
    """Prepare one item-store series for forecasting."""

    required_columns = {
        "date",
        "item_id",
        "store_id",
        "sales",
    }

    missing = required_columns - set(
        dataframe.columns
    )

    if missing:
        raise ValueError(
            f"Missing columns: {sorted(missing)}"
        )

    series = dataframe[
        (dataframe["item_id"].astype(str) == str(item_id))
        & (dataframe["store_id"].astype(str) == str(store_id))
    ].copy()

    if series.empty:
        raise ValueError(
            f"No data found for item={item_id}, "
            f"store={store_id}."
        )

    series = (
        series[
            ["date", "item_id", "store_id", "sales"]
        ]
        .groupby(
            ["date", "item_id", "store_id"],
            as_index=False,
        )
        .agg({"sales": "sum"})
        .sort_values("date")
        .reset_index(drop=True)
    )

    return series


def get_top_forecasting_series(
    dataframe: pd.DataFrame,
    top_n: int = 5,
) -> list[tuple[str, str]]:
    """Return top item-store combinations for model execution."""

    ranking = get_top_item_store_series(
        dataframe,
        top_n=top_n,
    )

    return [
        (
            str(row["item_id"]),
            str(row["store_id"]),
        )
        for _, row in ranking.iterrows()
    ]


def prepare_prophet_input(
    series: pd.DataFrame,
) -> pd.DataFrame:
    """Convert item-store sales into Prophet ds/y format."""

    if series.empty:
        raise ValueError(
            "Series cannot be empty."
        )

    output = series[
        ["date", "sales"]
    ].copy()

    output = output.rename(
        columns={
            "date": "ds",
            "sales": "y",
        }
    )

    output["ds"] = pd.to_datetime(
        output["ds"],
        errors="coerce",
    )

    output["y"] = pd.to_numeric(
        output["y"],
        errors="coerce",
    )

    output = output.dropna(
        subset=["ds", "y"]
    )

    output["y"] = output["y"].clip(
        lower=0
    )

    return output.sort_values(
        "ds"
    ).reset_index(drop=True)


def prepare_lightgbm_input(
    series: pd.DataFrame,
) -> pd.DataFrame:
    """Create basic time-series features for LightGBM."""

    if series.empty:
        raise ValueError(
            "Series cannot be empty."
        )

    output = series.copy()

    output["date"] = pd.to_datetime(
        output["date"],
        errors="coerce",
    )

    output["sales"] = pd.to_numeric(
        output["sales"],
        errors="coerce",
    )

    output = output.dropna(
        subset=["date", "sales"]
    ).sort_values("date")

    output["day_of_week"] = (
        output["date"].dt.dayofweek
    )

    output["day_of_month"] = (
        output["date"].dt.day
    )

    output["day_of_year"] = (
        output["date"].dt.dayofyear
    )

    output["week_of_year"] = (
        output["date"].dt.isocalendar().week
        .astype(int)
    )

    output["month_number"] = (
        output["date"].dt.month
    )

    output["quarter"] = (
        output["date"].dt.quarter
    )

    output["year_number"] = (
        output["date"].dt.year
    )

    output["is_weekend"] = (
        output["date"].dt.dayofweek >= 5
    ).astype(int)

    for lag in [1, 7, 14, 28]:
        output[f"lag_{lag}"] = (
            output["sales"].shift(lag)
        )

    for window in [7, 14, 28]:
        output[f"rolling_mean_{window}"] = (
            output["sales"]
            .shift(1)
            .rolling(window)
            .mean()
        )

        output[f"rolling_std_{window}"] = (
            output["sales"]
            .shift(1)
            .rolling(window)
            .std()
        )

    output["sell_price"] = 0.0
    output["price_change"] = 0.0
    output["price_change_7d"] = 0.0
    output["has_event"] = 0
    output["has_event_type"] = 0

    return output.reset_index(drop=True)