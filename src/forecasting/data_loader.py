import os
from typing import Optional

import pandas as pd
from google.cloud import bigquery


DEFAULT_TABLE = "fct_daily_sales"


def get_bigquery_client() -> bigquery.Client:
    """
    Create and return a BigQuery client.

    Authentication is expected to be configured through
    GOOGLE_APPLICATION_CREDENTIALS or the active Google Cloud
    authentication environment.
    """
    project_id = os.getenv("GCP_PROJECT_ID")

    if project_id:
        return bigquery.Client(project=project_id)

    return bigquery.Client()


def load_daily_sales(
    table_name: str = DEFAULT_TABLE,
    project_id: Optional[str] = None,
    dataset_id: Optional[str] = None,
) -> pd.DataFrame:
    """
    Load the Week 2 daily sales mart from BigQuery.

    Expected table:
        <project_id>.<dataset_id>.fct_daily_sales
    """

    project_id = project_id or os.getenv("GCP_PROJECT_ID")
    dataset_id = dataset_id or os.getenv(
        "BIGQUERY_MART_DATASET",
        "retail_demand_marts",
    )

    if not project_id:
        raise ValueError(
            "GCP_PROJECT_ID environment variable is required."
        )

    table_ref = f"`{project_id}.{dataset_id}.{table_name}`"

    query = f"""
        SELECT
            date,
            item_id,
            dept_id,
            cat_id,
            store_id,
            state_id,
            sales,
            sell_price,
            weekday,
            month,
            year,
            event,
            event_type
        FROM {table_ref}
        ORDER BY date, store_id, item_id
    """

    client = get_bigquery_client()
    dataframe = client.query(query).to_dataframe()

    if dataframe.empty:
        raise ValueError(
            f"No records were returned from {project_id}.{dataset_id}.{table_name}."
        )

    dataframe["date"] = pd.to_datetime(dataframe["date"])

    dataframe["sales"] = pd.to_numeric(
        dataframe["sales"],
        errors="coerce",
    )

    dataframe["sell_price"] = pd.to_numeric(
        dataframe["sell_price"],
        errors="coerce",
    )

    return dataframe

def load_forecasting_series(
    item_id: str,
    store_id: str,
    table_name: str = DEFAULT_TABLE,
    project_id: Optional[str] = None,
    dataset_id: Optional[str] = None,
) -> pd.DataFrame:
    """
    Load one item-store time series for forecasting.
    """

    project_id = project_id or os.getenv("GCP_PROJECT_ID")
    dataset_id = dataset_id or os.getenv(
        "BIGQUERY_MART_DATASET",
        "retail_demand_marts",
    )

    if not project_id:
        raise ValueError(
            "GCP_PROJECT_ID environment variable is required."
        )

    table_ref = f"{project_id}.{dataset_id}.{table_name}"

    query = f"""
        SELECT
            date,
            item_id,
            dept_id,
            cat_id,
            store_id,
            state_id,
            sales,
            sell_price,
            weekday,
            month,
            year,
            event,
            event_type
        FROM {table_ref}
        WHERE CAST(item_id AS STRING) = @item_id
          AND CAST(store_id AS STRING) = @store_id
        ORDER BY date
    """

    client = get_bigquery_client()

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter(
                "item_id",
                "STRING",
                str(item_id),
            ),
            bigquery.ScalarQueryParameter(
                "store_id",
                "STRING",
                str(store_id),
            ),
        ]
    )

    dataframe = client.query(
        query,
        job_config=job_config,
    ).to_dataframe()

    if dataframe.empty:
        raise ValueError(
            f"No data found for item_id={item_id}, "
            f"store_id={store_id}."
        )

    dataframe["date"] = pd.to_datetime(
        dataframe["date"],
        errors="coerce",
    )

    dataframe["sales"] = pd.to_numeric(
        dataframe["sales"],
        errors="coerce",
    )

    return dataframe


def validate_daily_sales(dataframe: pd.DataFrame) -> None:
    """
    Perform basic validation of the forecasting input dataset.
    """

    required_columns = {
        "date",
        "item_id",
        "store_id",
        "sales",
    }

    missing_columns = required_columns - set(dataframe.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    if dataframe["date"].isna().any():
        raise ValueError("Daily sales contains null dates.")

    if dataframe["item_id"].isna().any():
        raise ValueError("Daily sales contains null item_id values.")

    if dataframe["store_id"].isna().any():
        raise ValueError("Daily sales contains null store_id values.")

    if dataframe["sales"].isna().any():
        raise ValueError("Daily sales contains null sales values.")

    if (dataframe["sales"] < 0).any():
        raise ValueError("Daily sales contains negative sales values.")


if __name__ == "__main__":
    df = load_daily_sales()
    validate_daily_sales(df)

    print("Forecasting dataset loaded successfully.")
    print(f"Rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")