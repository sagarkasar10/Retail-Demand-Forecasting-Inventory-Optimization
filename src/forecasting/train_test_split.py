import pandas as pd


def chronological_split(
    dataframe: pd.DataFrame,
    validation_days: int = 30,
    test_days: int = 30,
):
    """
    Split time-series data chronologically.
    """

    if dataframe.empty:
        raise ValueError("Cannot split an empty dataframe.")

    if validation_days <= 0:
        raise ValueError("validation_days must be greater than zero.")

    if test_days <= 0:
        raise ValueError("test_days must be greater than zero.")

    if "date" not in dataframe.columns:
        raise ValueError("Dataframe must contain a 'date' column.")

    df = dataframe.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    if df["date"].isna().any():
        raise ValueError("Dataframe contains invalid dates.")

    df = df.sort_values("date").reset_index(drop=True)

    unique_dates = pd.Series(
        df["date"].dt.normalize().unique()
    ).sort_values().tolist()

    required_dates = validation_days + test_days + 1

    if len(unique_dates) < required_dates:
        raise ValueError(
            "Not enough historical dates for the requested "
            "train, validation, and test periods."
        )

    train_end = len(unique_dates) - validation_days - test_days
    validation_end = len(unique_dates) - test_days

    train_dates = set(unique_dates[:train_end])
    validation_dates = set(
        unique_dates[train_end:validation_end]
    )
    test_dates = set(unique_dates[validation_end:])

    normalized_dates = df["date"].dt.normalize()

    train_df = df[normalized_dates.isin(train_dates)].copy()
    validation_df = df[
        normalized_dates.isin(validation_dates)
    ].copy()
    test_df = df[
        normalized_dates.isin(test_dates)
    ].copy()

    if train_df.empty:
        raise ValueError("Training dataset is empty.")

    if validation_df.empty:
        raise ValueError("Validation dataset is empty.")

    if test_df.empty:
        raise ValueError("Test dataset is empty.")

    return (
        train_df.reset_index(drop=True),
        validation_df.reset_index(drop=True),
        test_df.reset_index(drop=True),
    )


def create_forecast_window(
    dataframe: pd.DataFrame,
    forecast_horizon: int = 30,
) -> pd.DataFrame:
    """
    Return the most recent forecast horizon from a dataframe.
    """

    if dataframe.empty:
        raise ValueError("Cannot create a forecast window from empty data.")

    if forecast_horizon <= 0:
        raise ValueError(
            "forecast_horizon must be greater than zero."
        )

    df = dataframe.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    if df["date"].isna().any():
        raise ValueError("Dataframe contains invalid dates.")

    return (
        df.sort_values("date")
        .tail(forecast_horizon)
        .reset_index(drop=True)
    )


def get_split_summary(
    train_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    test_df: pd.DataFrame,
) -> dict:
    """
    Return date ranges and row counts for each split.
    """

    return {
        "train": {
            "rows": len(train_df),
            "start_date": train_df["date"].min(),
            "end_date": train_df["date"].max(),
        },
        "validation": {
            "rows": len(validation_df),
            "start_date": validation_df["date"].min(),
            "end_date": validation_df["date"].max(),
        },
        "test": {
            "rows": len(test_df),
            "start_date": test_df["date"].min(),
            "end_date": test_df["date"].max(),
        },
    }