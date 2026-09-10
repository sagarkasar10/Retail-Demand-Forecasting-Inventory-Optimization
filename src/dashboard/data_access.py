from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

import pandas as pd
from google.cloud import bigquery


# -----------------------------
# Configuration
# -----------------------------

PROJECT_ID = (
    os.getenv("GCP_PROJECT_ID")
    or os.getenv("GOOGLE_CLOUD_PROJECT")
)

FORECAST_DATASET = os.getenv(
    "FORECAST_DATASET",
    "retail_demand"
)

MARTS_DATASET = os.getenv(
    "MARTS_DATASET",
    "retail_demand"
)

FORECAST_TABLE = os.getenv(
    "FORECAST_TABLE",
    "forecast_results"
)

METRICS_TABLE = os.getenv(
    "METRICS_TABLE",
    "forecast_metrics"
)

MODEL_RUNS_TABLE = os.getenv(
    "MODEL_RUNS_TABLE",
    "model_runs"
)

DAILY_SALES_TABLE = os.getenv(
    "DAILY_SALES_TABLE",
    "daily_sales"
)


# -----------------------------
# BigQuery helpers
# -----------------------------

def get_bigquery_client() -> bigquery.Client:
    """Create and return a BigQuery client."""

    if not PROJECT_ID:
        raise ValueError(
            "GCP_PROJECT_ID or GOOGLE_CLOUD_PROJECT "
            "environment variable must be configured."
        )

    return bigquery.Client(project=PROJECT_ID)


def _table_reference(
    table_name: str,
    dataset_name: str
) -> str:
    """Build a fully-qualified BigQuery table reference."""

    if not PROJECT_ID:
        raise ValueError(
            "GCP_PROJECT_ID or GOOGLE_CLOUD_PROJECT "
            "environment variable must be configured."
        )

    return f"`{PROJECT_ID}.{dataset_name}.{table_name}`"


def _execute_query(
    query: str,
    parameters: Optional[list] = None
) -> pd.DataFrame:
    """Execute a parameterized BigQuery query."""

    client = get_bigquery_client()

    job_config = bigquery.QueryJobConfig()

    if parameters:
        job_config.query_parameters = parameters

    query_job = client.query(
        query,
        job_config=job_config
    )

    return query_job.result().to_dataframe()


# -----------------------------
# Available filters
# -----------------------------

@lru_cache(maxsize=1)
def get_available_stores() -> list[str]:
    """Return available store IDs."""

    query = f"""
        SELECT DISTINCT
            CAST(store_id AS STRING) AS store_id
        FROM {_table_reference(
            DAILY_SALES_TABLE,
            MARTS_DATASET
        )}
        WHERE store_id IS NOT NULL
        ORDER BY store_id
    """

    df = _execute_query(query)

    return df["store_id"].astype(str).tolist()


@lru_cache(maxsize=1)
def get_available_departments() -> list[str]:
    """Return available department IDs."""

    query = f"""
        SELECT DISTINCT
            CAST(dept_id AS STRING) AS dept_id
        FROM {_table_reference(
            DAILY_SALES_TABLE,
            MARTS_DATASET
        )}
        WHERE dept_id IS NOT NULL
        ORDER BY dept_id
    """

    df = _execute_query(query)

    return df["dept_id"].astype(str).tolist()


@lru_cache(maxsize=1)
def get_available_categories() -> list[str]:
    """Return available category IDs."""

    query = f"""
        SELECT DISTINCT
            CAST(cat_id AS STRING) AS cat_id
        FROM {_table_reference(
            DAILY_SALES_TABLE,
            MARTS_DATASET
        )}
        WHERE cat_id IS NOT NULL
        ORDER BY cat_id
    """

    df = _execute_query(query)

    return df["cat_id"].astype(str).tolist()


@lru_cache(maxsize=1)
def get_available_items() -> list[str]:
    """Return available item IDs."""

    query = f"""
        SELECT DISTINCT
            CAST(item_id AS STRING) AS item_id
        FROM {_table_reference(
            DAILY_SALES_TABLE,
            MARTS_DATASET
        )}
        WHERE item_id IS NOT NULL
        ORDER BY item_id
    """

    df = _execute_query(query)

    return df["item_id"].astype(str).tolist()


@lru_cache(maxsize=1)
def get_available_models() -> list[str]:
    """Return available forecasting models."""

    query = f"""
        SELECT DISTINCT
            CAST(model_name AS STRING) AS model_name
        FROM {_table_reference(
            FORECAST_TABLE,
            FORECAST_DATASET
        )}
        WHERE model_name IS NOT NULL
        ORDER BY model_name
    """

    df = _execute_query(query)

    return df["model_name"].astype(str).tolist()


# -----------------------------
# Forecast data
# -----------------------------

def get_forecast_data(
    store_id: Optional[str] = None,
    dept_id: Optional[str] = None,
    cat_id: Optional[str] = None,
    item_id: Optional[str] = None,
    model_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> pd.DataFrame:
    """Retrieve filtered forecast data."""

    conditions = ["forecast_date IS NOT NULL"]
    parameters = []

    filters = {
        "store_id": store_id,
        "dept_id": dept_id,
        "cat_id": cat_id,
        "item_id": item_id,
        "model_name": model_name,
    }

    for field, value in filters.items():
        if value:
            conditions.append(
                f"CAST({field} AS STRING) = @{field}"
            )

            parameters.append(
                bigquery.ScalarQueryParameter(
                    field,
                    "STRING",
                    str(value)
                )
            )

    if start_date:
        conditions.append(
            "forecast_date >= @start_date"
        )

        parameters.append(
            bigquery.ScalarQueryParameter(
                "start_date",
                "DATE",
                start_date
            )
        )

    if end_date:
        conditions.append(
            "forecast_date <= @end_date"
        )

        parameters.append(
            bigquery.ScalarQueryParameter(
                "end_date",
                "DATE",
                end_date
            )
        )

    query = f"""
        SELECT
            forecast_date,
            store_id,
            item_id,
            dept_id,
            cat_id,
            model_name,
            predicted_demand,
            actual_demand,
            run_id,
            created_at
        FROM {_table_reference(
            FORECAST_TABLE,
            FORECAST_DATASET
        )}
        WHERE {" AND ".join(conditions)}
        ORDER BY forecast_date
    """

    return _execute_query(
        query,
        parameters
    )


# -----------------------------
# Latest forecast
# -----------------------------

def get_latest_forecast_run() -> Optional[str]:
    """Return the latest completed forecast run ID."""

    query = f"""
        SELECT run_id
        FROM {_table_reference(
            MODEL_RUNS_TABLE,
            FORECAST_DATASET
        )}
        WHERE status = 'completed'
        ORDER BY created_at DESC
        LIMIT 1
    """

    df = _execute_query(query)

    if df.empty:
        return None

    return str(df.iloc[0]["run_id"])


# -----------------------------
# Forecast date range
# -----------------------------

def get_forecast_date_range() -> tuple:
    """Return minimum and maximum forecast dates."""

    query = f"""
        SELECT
            MIN(forecast_date) AS min_date,
            MAX(forecast_date) AS max_date
        FROM {_table_reference(
            FORECAST_TABLE,
            FORECAST_DATASET
        )}
    """

    df = _execute_query(query)

    if df.empty:
        return None, None

    return (
        df.iloc[0]["min_date"],
        df.iloc[0]["max_date"]
    )


# -----------------------------
# Daily sales
# -----------------------------

def get_daily_sales(
    store_id: Optional[str] = None,
    item_id: Optional[str] = None,
    dept_id: Optional[str] = None,
    cat_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> pd.DataFrame:
    """Retrieve historical daily sales."""

    conditions = ["date IS NOT NULL"]
    parameters = []

    filters = {
        "store_id": store_id,
        "item_id": item_id,
        "dept_id": dept_id,
        "cat_id": cat_id,
    }

    for field, value in filters.items():
        if value:
            conditions.append(
                f"CAST({field} AS STRING) = @{field}"
            )

            parameters.append(
                bigquery.ScalarQueryParameter(
                    field,
                    "STRING",
                    str(value)
                )
            )

    if start_date:
        conditions.append(
            "date >= @sales_start_date"
        )

        parameters.append(
            bigquery.ScalarQueryParameter(
                "sales_start_date",
                "DATE",
                start_date
            )
        )

    if end_date:
        conditions.append(
            "date <= @sales_end_date"
        )

        parameters.append(
            bigquery.ScalarQueryParameter(
                "sales_end_date",
                "DATE",
                end_date
            )
        )

    query = f"""
        SELECT
            date,
            store_id,
            item_id,
            dept_id,
            cat_id,
            state_id,
            sales,
            sell_price
        FROM {_table_reference(
            DAILY_SALES_TABLE,
            MARTS_DATASET
        )}
        WHERE {" AND ".join(conditions)}
        ORDER BY date
    """

    return _execute_query(
        query,
        parameters
    )


# -----------------------------
# Forecast metrics
# -----------------------------

def get_forecast_metrics(
    model_name: Optional[str] = None
) -> pd.DataFrame:
    """Retrieve model evaluation metrics."""

    conditions = []
    parameters = []

    if model_name:
        conditions.append(
            "model_name = @model_name"
        )

        parameters.append(
            bigquery.ScalarQueryParameter(
                "model_name",
                "STRING",
                str(model_name)
            )
        )

    where_clause = ""

    if conditions:
        where_clause = (
            "WHERE " +
            " AND ".join(conditions)
        )

    query = f"""
        SELECT
            model_name,
            mae,
            rmse,
            mape,
            r2_score,
            evaluated_at
        FROM {_table_reference(
            METRICS_TABLE,
            FORECAST_DATASET
        )}
        {where_clause}
        ORDER BY mae ASC
    """

    return _execute_query(
        query,
        parameters
    )


# -----------------------------
# Model runs
# -----------------------------

def get_model_runs() -> pd.DataFrame:
    """Retrieve model execution history."""

    query = f"""
        SELECT
            run_id,
            model_name,
            status,
            created_at,
            completed_at
        FROM {_table_reference(
            MODEL_RUNS_TABLE,
            FORECAST_DATASET
        )}
        ORDER BY created_at DESC
    """

    return _execute_query(query)