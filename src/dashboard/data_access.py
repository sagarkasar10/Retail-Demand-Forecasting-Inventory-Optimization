from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

import pandas as pd
from google.cloud import bigquery


PROJECT_ID = os.getenv("GCP_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")

FORECAST_DATASET = os.getenv(
    "FORECAST_DATASET",
    "retail_demand_forecasting",
)

MARTS_DATASET = os.getenv(
    "MARTS_DATASET",
    "retail_demand_marts",
)

FORECAST_TABLE = os.getenv(
    "FORECAST_TABLE",
    "forecast_predictions",
)

METRICS_TABLE = os.getenv(
    "METRICS_TABLE",
    "forecast_metrics",
)

MODEL_RUNS_TABLE = os.getenv(
    "MODEL_RUNS_TABLE",
    "model_runs",
)

DAILY_SALES_TABLE = os.getenv(
    "DAILY_SALES_TABLE",
    "fct_daily_sales",
)


def get_bigquery_client() -> bigquery.Client:
    """
    Create and return a BigQuery client.

    Authentication is expected to be configured through the
    Google Cloud environment or application credentials.
    """
    if not PROJECT_ID:
        raise RuntimeError(
            "GCP_PROJECT_ID or GOOGLE_CLOUD_PROJECT environment "
            "variable is not configured."
        )

    return bigquery.Client(project=PROJECT_ID)


def _table_reference(dataset: str, table: str) -> str:
    """
    Return a fully qualified BigQuery table reference.
    """
    if not PROJECT_ID:
        raise RuntimeError(
            "GCP_PROJECT_ID or GOOGLE_CLOUD_PROJECT environment "
            "variable is not configured."
        )

    return f"`{PROJECT_ID}.{dataset}.{table}`"


def _execute_query(
    query: str,
    parameters: Optional[list] = None,
) -> pd.DataFrame:
    """
    Execute a BigQuery query and return the result as a DataFrame.
    """
    client = get_bigquery_client()

    job_config = bigquery.QueryJobConfig()

    if parameters:
        job_config.query_parameters = parameters

    query_job = client.query(
        query,
        job_config=job_config,
    )

    return query_job.result().to_dataframe()


@lru_cache(maxsize=1)
def get_available_stores() -> list[str]:
    """
    Return available store IDs.
    """
    query = f"""
        SELECT DISTINCT
            CAST(store_id AS STRING) AS store_id
        FROM {_table_reference(MARTS_DATASET, DAILY_SALES_TABLE)}
        WHERE store_id IS NOT NULL
        ORDER BY store_id
    """

    df = _execute_query(query)

    return df["store_id"].astype(str).tolist()


@lru_cache(maxsize=1)
def get_available_departments() -> list[str]:
    """
    Return available department IDs.
    """
    query = f"""
        SELECT DISTINCT
            CAST(dept_id AS STRING) AS dept_id
        FROM {_table_reference(MARTS_DATASET, DAILY_SALES_TABLE)}
        WHERE dept_id IS NOT NULL
        ORDER BY dept_id
    """

    df = _execute_query(query)

    return df["dept_id"].astype(str).tolist()


@lru_cache(maxsize=1)
def get_available_categories() -> list[str]:
    """
    Return available category IDs.
    """
    query = f"""
        SELECT DISTINCT
            CAST(cat_id AS STRING) AS cat_id
        FROM {_table_reference(MARTS_DATASET, DAILY_SALES_TABLE)}
        WHERE cat_id IS NOT NULL
        ORDER BY cat_id
    """

    df = _execute_query(query)

    return df["cat_id"].astype(str).tolist()


@lru_cache(maxsize=1)
def get_available_items() -> list[str]:
    """
    Return available item IDs.
    """
    query = f"""
        SELECT DISTINCT
            CAST(item_id AS STRING) AS item_id
        FROM {_table_reference(MARTS_DATASET, DAILY_SALES_TABLE)}
        WHERE item_id IS NOT NULL
        ORDER BY item_id
    """

    df = _execute_query(query)

    return df["item_id"].astype(str).tolist()


def get_forecast_data(
    store_id: Optional[str] = None,
    item_id: Optional[str] = None,
    dept_id: Optional[str] = None,
    cat_id: Optional[str] = None,
    model_name: Optional[str] = None,
) -> pd.DataFrame:
    """
    Retrieve forecast predictions from BigQuery.

    Filters are optional. None means no filtering for that field.
    """
    conditions = ["1 = 1"]
    parameters = []

    if store_id:
        conditions.append("CAST(store_id AS STRING) = @store_id")
        parameters.append(
            bigquery.ScalarQueryParameter(
                "store_id",
                "STRING",
                str(store_id),
            )
        )

    if item_id:
        conditions.append("CAST(item_id AS STRING) = @item_id")
        parameters.append(
            bigquery.ScalarQueryParameter(
                "item_id",
                "STRING",
                str(item_id),
            )
        )

    if dept_id:
        conditions.append("CAST(dept_id AS STRING) = @dept_id")
        parameters.append(
            bigquery.ScalarQueryParameter(
                "dept_id",
                "STRING",
                str(dept_id),
            )
        )

    if cat_id:
        conditions.append("CAST(cat_id AS STRING) = @cat_id")
        parameters.append(
            bigquery.ScalarQueryParameter(
                "cat_id",
                "STRING",
                str(cat_id),
            )
        )

    if model_name:
        conditions.append("model_name = @model_name")
        parameters.append(
            bigquery.ScalarQueryParameter(
                "model_name",
                "STRING",
                str(model_name),
            )
        )

    query = f"""
        SELECT
            CAST(forecast_date AS DATE) AS forecast_date,
            CAST(store_id AS STRING) AS store_id,
            CAST(item_id AS STRING) AS item_id,
            CAST(dept_id AS STRING) AS dept_id,
            CAST(cat_id AS STRING) AS cat_id,
            CAST(model_name AS STRING) AS model_name,
            CAST(predicted_demand AS FLOAT64) AS predicted_demand,
            CAST(actual_demand AS FLOAT64) AS actual_demand,
            CAST(run_id AS STRING) AS run_id,
            created_at
        FROM {_table_reference(FORECAST_DATASET, FORECAST_TABLE)}
        WHERE {" AND ".join(conditions)}
        ORDER BY forecast_date
    """

    return _execute_query(query, parameters)


def get_forecast_metrics(
    model_name: Optional[str] = None,
) -> pd.DataFrame:
    """
    Retrieve model evaluation metrics.
    """
    conditions = ["1 = 1"]
    parameters = []

    if model_name:
        conditions.append("model_name = @model_name")
        parameters.append(
            bigquery.ScalarQueryParameter(
                "model_name",
                "STRING",
                str(model_name),
            )
        )

    query = f"""
        SELECT
            CAST(run_id AS STRING) AS run_id,
            CAST(model_name AS STRING) AS model_name,
            CAST(forecast_level AS STRING) AS forecast_level,
            CAST(mae AS FLOAT64) AS mae,
            CAST(rmse AS FLOAT64) AS rmse,
            CAST(mape AS FLOAT64) AS mape,
            CAST(wape AS FLOAT64) AS wape,
            training_start_date,
            training_end_date,
            evaluation_start_date,
            evaluation_end_date,
            created_at
        FROM {_table_reference(FORECAST_DATASET, METRICS_TABLE)}
        WHERE {" AND ".join(conditions)}
        ORDER BY created_at DESC
    """

    return _execute_query(query, parameters)


def get_model_runs() -> pd.DataFrame:
    """
    Retrieve model execution metadata.
    """
    query = f"""
        SELECT
            CAST(run_id AS STRING) AS run_id,
            CAST(model_name AS STRING) AS model_name,
            CAST(model_version AS STRING) AS model_version,
            training_start_date,
            training_end_date,
            CAST(forecast_horizon AS INT64) AS forecast_horizon,
            CAST(feature_version AS STRING) AS feature_version,
            CAST(status AS STRING) AS status,
            created_at
        FROM {_table_reference(FORECAST_DATASET, MODEL_RUNS_TABLE)}
        ORDER BY created_at DESC
    """

    return _execute_query(query)


def get_latest_forecast_run() -> pd.DataFrame:
    """
    Return forecast predictions belonging to the latest model run.
    """
    query = f"""
        WITH latest_run AS (
            SELECT
                run_id
            FROM {_table_reference(FORECAST_DATASET, MODEL_RUNS_TABLE)}
            WHERE status = 'success'
            ORDER BY created_at DESC
            LIMIT 1
        )

        SELECT
            CAST(forecast_date AS DATE) AS forecast_date,
            CAST(store_id AS STRING) AS store_id,
            CAST(item_id AS STRING) AS item_id,
            CAST(dept_id AS STRING) AS dept_id,
            CAST(cat_id AS STRING) AS cat_id,
            CAST(model_name AS STRING) AS model_name,
            CAST(predicted_demand AS FLOAT64) AS predicted_demand,
            CAST(actual_demand AS FLOAT64) AS actual_demand,
            CAST(run_id AS STRING) AS run_id,
            created_at
        FROM {_table_reference(FORECAST_DATASET, FORECAST_TABLE)}
        WHERE run_id IN (
            SELECT run_id
            FROM latest_run
        )
        ORDER BY forecast_date
    """

    return _execute_query(query)


def get_daily_sales(
    store_id: Optional[str] = None,
    item_id: Optional[str] = None,
    dept_id: Optional[str] = None,
    cat_id: Optional[str] = None,
) -> pd.DataFrame:
    """
    Retrieve historical daily sales from the Week 2 mart.
    """
    conditions = ["1 = 1"]
    parameters = []

    filters = {
        "store_id": store_id,
        "item_id": item_id,
        "dept_id": dept_id,
        "cat_id": cat_id,
    }

    for column, value in filters.items():
        if value:
            parameter_name = column

            conditions.append(
                f"CAST({column} AS STRING) = @{parameter_name}"
            )

            parameters.append(
                bigquery.ScalarQueryParameter(
                    parameter_name,
                    "STRING",
                    str(value),
                )
            )

    query = f"""
        SELECT
            CAST(date AS DATE) AS date,
            CAST(store_id AS STRING) AS store_id,
            CAST(item_id AS STRING) AS item_id,
            CAST(dept_id AS STRING) AS dept_id,
            CAST(cat_id AS STRING) AS cat_id,
            CAST(state_id AS STRING) AS state_id,
            CAST(sales AS FLOAT64) AS sales,
            CAST(sell_price AS FLOAT64) AS sell_price
        FROM {_table_reference(MARTS_DATASET, DAILY_SALES_TABLE)}
        WHERE {" AND ".join(conditions)}
        ORDER BY date
    """

    return _execute_query(query, parameters)