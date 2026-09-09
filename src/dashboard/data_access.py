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
    """
    if not PROJECT_ID:
        raise RuntimeError(
            "GCP_PROJECT_ID or GOOGLE_CLOUD_PROJECT "
            "environment variable is not configured."
        )

    return bigquery.Client(project=PROJECT_ID)


def _table_reference(
    dataset: str,
    table: str,
) -> str:
    """
    Return a fully qualified BigQuery table reference.
    """
    if not PROJECT_ID:
        raise RuntimeError(
            "GCP_PROJECT_ID or GOOGLE_CLOUD_PROJECT "
            "environment variable is not configured."
        )

    return f"`{PROJECT_ID}.{dataset}.{table}`"


def _execute_query(
    query: str,
    parameters: Optional[list] = None,
) -> pd.DataFrame:
    """
    Execute a BigQuery query and return a DataFrame.
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
    Return all available store IDs.
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
    Return all available department IDs.
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
    Return all available category IDs.
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
    Return all available item IDs.
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


@lru_cache(maxsize=1)
def get_available_models() -> list[str]:
    """
    Return all forecast model names.
    """
    query = f"""
        SELECT DISTINCT
            CAST(model_name AS STRING) AS model_name
        FROM {_table_reference(FORECAST_DATASET, FORECAST_TABLE)}
        WHERE model_name IS NOT NULL
        ORDER BY model_name
    """

    df = _execute_query(query)

    return df["model_name"].astype(str).tolist()


def get_forecast_data(
    store_id: Optional[str] = None,
    item_id: Optional[str] = None,
    dept_id: Optional[str] = None,
    cat_id: Optional[str] = None,
    model_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """
    Retrieve filtered forecast predictions from BigQuery.

    All filters are optional.
    """
    conditions = ["1 = 1"]
    parameters = []

    if store_id:
        conditions.append(
            "CAST(store_id AS STRING) = @store_id"
        )
        parameters.append(
            bigquery.ScalarQueryParameter(
                "store_id",
                "STRING",
                str(store_id),
            )
        )

    if item_id:
        conditions.append(
            "CAST(item_id AS STRING) = @item_id"
        )
        parameters.append(
            bigquery.ScalarQueryParameter(
                "item_id",
                "STRING",
                str(item_id),
            )
        )

    if dept_id:
        conditions.append(
            "CAST(dept_id AS STRING) = @dept_id"
        )
        parameters.append(
            bigquery.ScalarQueryParameter(
                "dept_id",
                "STRING",
                str(dept_id),
            )
        )

    if cat_id:
        conditions.append(
            "CAST(cat_id AS STRING) = @cat_id"
        )
        parameters.append(
            bigquery.ScalarQueryParameter(
                "cat_id",
                "STRING",
                str(cat_id),
            )
        )

    if model_name:
        conditions.append(
            "model_name = @model_name"
        )
        parameters.append(
            bigquery.ScalarQueryParameter(
                "model_name",
                "STRING",
                str(model_name),
            )
        )

    if start_date:
        conditions.append(
            "CAST(forecast_date AS DATE) >= @start_date"
        )
        parameters.append(
            bigquery.ScalarQueryParameter(
                "start_date",
                "DATE",
                start_date,
            )
        )

    if end_date:
        conditions.append(
            "CAST(forecast_date AS DATE) <= @end_date"
        )
        parameters.append(
            bigquery.ScalarQueryParameter(
                "end_date",
                "DATE",
                end_date,
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
            CAST(predicted_demand AS FLOAT64)
                AS predicted_demand,
            CAST(actual_demand AS FLOAT64)
                AS actual_demand,
            CAST(run_id AS STRING) AS run_id,
            created_at
        FROM {_table_reference(
            FORECAST_DATASET,
            FORECAST_TABLE,
        )}
        WHERE {" AND ".join(conditions)}
        ORDER BY forecast_date
    """

    return _execute_query(
        query,
        parameters,
    )


def get_latest_forecast_run() -> pd.DataFrame:
    """
    Retrieve forecasts belonging to the latest successful run.
    """
    query = f"""
        WITH latest_run AS (
            SELECT
                run_id
            FROM {_table_reference(
                FORECAST_DATASET,
                MODEL_RUNS_TABLE,
            )}
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
            CAST(predicted_demand AS FLOAT64)
                AS predicted_demand,
            CAST(actual_demand AS FLOAT64)
                AS actual_demand,
            CAST(run_id AS STRING) AS run_id,
            created_at
        FROM {_table_reference(
            FORECAST_DATASET,
            FORECAST_TABLE,
        )}
        WHERE run_id IN (
            SELECT run_id
            FROM latest_run
        )
        ORDER BY forecast_date
    """

    return _execute_query(query)


def get_forecast_date_range() -> tuple:
    """
    Return minimum and maximum forecast dates.
    """
    query = f"""
        SELECT
            MIN(CAST(forecast_date AS DATE)) AS min_date,
            MAX(CAST(forecast_date AS DATE)) AS max_date
        FROM {_table_reference(
            FORECAST_DATASET,
            FORECAST_TABLE,
        )}
    """

    df = _execute_query(query)

    if df.empty:
        return None, None

    return (
        df.iloc[0]["min_date"],
        df.iloc[0]["max_date"],
    )


def get_daily_sales(
    store_id: Optional[str] = None,
    item_id: Optional[str] = None,
    dept_id: Optional[str] = None,
    cat_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """
    Retrieve historical daily sales.
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
            conditions.append(
                f"CAST({column} AS STRING) = @{column}"
            )

            parameters.append(
                bigquery.ScalarQueryParameter(
                    column,
                    "STRING",
                    str(value),
                )
            )

    if start_date:
        conditions.append(
            "CAST(date AS DATE) >= @sales_start_date"
        )
        parameters.append(
            bigquery.ScalarQueryParameter(
                "sales_start_date",
                "DATE",
                start_date,
            )
        )

    if end_date:
        conditions.append(
            "CAST(date AS DATE) <= @sales_end_date"
        )
        parameters.append(
            bigquery.ScalarQueryParameter(
                "sales_end_date",
                "DATE",
                end_date,
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
        FROM {_table_reference(
            MARTS_DATASET,
            DAILY_SALES_TABLE,
        )}
        WHERE {" AND ".join(conditions)}
        ORDER BY date
    """

    return _execute_query(
        query,
        parameters,
    )


import os
from typing import Optional

import pandas as pd
from google.cloud import bigquery


def get_bigquery_client() -> bigquery.Client:
    """
    Create and return a BigQuery client.

    Google Cloud authentication is handled through the environment
    configured for the project.
    """
    project_id = (
        os.getenv("GCP_PROJECT_ID")
        or os.getenv("GOOGLE_CLOUD_PROJECT")
    )

    if not project_id:
        raise ValueError(
            "GCP_PROJECT_ID or GOOGLE_CLOUD_PROJECT environment variable "
            "must be configured."
        )

    return bigquery.Client(project=project_id)


def _get_project_id() -> str:
    project_id = (
        os.getenv("GCP_PROJECT_ID")
        or os.getenv("GOOGLE_CLOUD_PROJECT")
    )

    if not project_id:
        raise ValueError(
            "GCP_PROJECT_ID or GOOGLE_CLOUD_PROJECT environment variable "
            "must be configured."
        )

    return project_id


def _table_reference(table_name: str, dataset_name: str) -> str:
    """
    Build a fully-qualified BigQuery table reference.
    """
    project_id = _get_project_id()

    return f"`{project_id}.{dataset_name}.{table_name}`"


def _execute_query(
    query: str,
    query_parameters: Optional[list] = None
) -> pd.DataFrame:
    """
    Execute a parameterized BigQuery query and return a DataFrame.
    """
    client = get_bigquery_client()

    job_config = bigquery.QueryJobConfig()

    if query_parameters:
        job_config.query_parameters = query_parameters

    query_job = client.query(
        query,
        job_config=job_config
    )

    return query_job.result().to_dataframe()


def _get_dataset_name(environment_variable: str, default: str) -> str:
    return os.getenv(environment_variable, default)


def get_available_stores() -> list:
    """
    Return distinct store IDs available in forecast data.
    """
    dataset = _get_dataset_name("FORECAST_DATASET", "retail_demand")
    table = os.getenv("FORECAST_TABLE", "forecast_results")

    query = f"""
        SELECT DISTINCT store_id
        FROM {_table_reference(table, dataset)}
        WHERE store_id IS NOT NULL
        ORDER BY store_id
    """

    df = _execute_query(query)

    return df["store_id"].dropna().astype(str).tolist()


def get_available_departments() -> list:
    """
    Return distinct department IDs available in forecast data.
    """
    dataset = _get_dataset_name("FORECAST_DATASET", "retail_demand")
    table = os.getenv("FORECAST_TABLE", "forecast_results")

    query = f"""
        SELECT DISTINCT dept_id
        FROM {_table_reference(table, dataset)}
        WHERE dept_id IS NOT NULL
        ORDER BY dept_id
    """

    df = _execute_query(query)

    return df["dept_id"].dropna().astype(str).tolist()


def get_available_categories() -> list:
    """
    Return distinct category IDs available in forecast data.
    """
    dataset = _get_dataset_name("FORECAST_DATASET", "retail_demand")
    table = os.getenv("FORECAST_TABLE", "forecast_results")

    query = f"""
        SELECT DISTINCT cat_id
        FROM {_table_reference(table, dataset)}
        WHERE cat_id IS NOT NULL
        ORDER BY cat_id
    """

    df = _execute_query(query)

    return df["cat_id"].dropna().astype(str).tolist()


def get_available_items(
    store_id: Optional[str] = None,
    dept_id: Optional[str] = None,
    cat_id: Optional[str] = None
) -> list:
    """
    Return items based on optional dashboard filters.
    """
    dataset = _get_dataset_name("FORECAST_DATASET", "retail_demand")
    table = os.getenv("FORECAST_TABLE", "forecast_results")

    conditions = [
        "item_id IS NOT NULL"
    ]

    parameters = []

    if store_id:
        conditions.append("store_id = @store_id")
        parameters.append(
            bigquery.ScalarQueryParameter(
                "store_id",
                "STRING",
                store_id
            )
        )

    if dept_id:
        conditions.append("dept_id = @dept_id")
        parameters.append(
            bigquery.ScalarQueryParameter(
                "dept_id",
                "STRING",
                dept_id
            )
        )

    if cat_id:
        conditions.append("cat_id = @cat_id")
        parameters.append(
            bigquery.ScalarQueryParameter(
                "cat_id",
                "STRING",
                cat_id
            )
        )

    query = f"""
        SELECT DISTINCT item_id
        FROM {_table_reference(table, dataset)}
        WHERE {" AND ".join(conditions)}
        ORDER BY item_id
    """

    df = _execute_query(
        query,
        parameters
    )

    return df["item_id"].dropna().astype(str).tolist()


def get_available_models() -> list:
    """
    Return distinct forecasting model names.
    """
    dataset = _get_dataset_name("FORECAST_DATASET", "retail_demand")
    table = os.getenv("FORECAST_TABLE", "forecast_results")

    query = f"""
        SELECT DISTINCT model_name
        FROM {_table_reference(table, dataset)}
        WHERE model_name IS NOT NULL
        ORDER BY model_name
    """

    df = _execute_query(query)

    return df["model_name"].dropna().astype(str).tolist()


def get_forecast_data(
    store_id: Optional[str] = None,
    dept_id: Optional[str] = None,
    cat_id: Optional[str] = None,
    item_id: Optional[str] = None,
    model_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> pd.DataFrame:
    """
    Retrieve forecast data using dashboard filters.
    """
    dataset = _get_dataset_name("FORECAST_DATASET", "retail_demand")
    table = os.getenv("FORECAST_TABLE", "forecast_results")

    conditions = [
        "forecast_date IS NOT NULL"
    ]

    parameters = []

    filter_values = [
        ("store_id", store_id),
        ("dept_id", dept_id),
        ("cat_id", cat_id),
        ("item_id", item_id),
        ("model_name", model_name),
    ]

    for field, value in filter_values:
        if value:
            conditions.append(f"{field} = @{field}")
            parameters.append(
                bigquery.ScalarQueryParameter(
                    field,
                    "STRING",
                    value
                )
            )

    if start_date:
        conditions.append("forecast_date >= @start_date")
        parameters.append(
            bigquery.ScalarQueryParameter(
                "start_date",
                "DATE",
                start_date
            )
        )

    if end_date:
        conditions.append("forecast_date <= @end_date")
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
        FROM {_table_reference(table, dataset)}
        WHERE {" AND ".join(conditions)}
        ORDER BY forecast_date
    """

    return _execute_query(
        query,
        parameters
    )


def get_latest_forecast_run() -> Optional[str]:
    """
    Return the latest completed forecast run ID.
    """
    dataset = _get_dataset_name("FORECAST_DATASET", "retail_demand")
    table = os.getenv("MODEL_RUNS_TABLE", "model_runs")

    query = f"""
        SELECT run_id
        FROM {_table_reference(table, dataset)}
        WHERE status = 'completed'
        ORDER BY created_at DESC
        LIMIT 1
    """

    df = _execute_query(query)

    if df.empty:
        return None

    return str(df.iloc[0]["run_id"])


def get_forecast_date_range() -> tuple:
    """
    Return minimum and maximum forecast dates.
    """
    dataset = _get_dataset_name("FORECAST_DATASET", "retail_demand")
    table = os.getenv("FORECAST_TABLE", "forecast_results")

    query = f"""
        SELECT
            MIN(forecast_date) AS min_date,
            MAX(forecast_date) AS max_date
        FROM {_table_reference(table, dataset)}
    """

    df = _execute_query(query)

    if df.empty:
        return None, None

    return (
        df.iloc[0]["min_date"],
        df.iloc[0]["max_date"]
    )


def get_daily_sales(
    store_id: Optional[str] = None,
    item_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> pd.DataFrame:
    """
    Retrieve historical daily sales for inventory calculations.
    """
    dataset = _get_dataset_name("MARTS_DATASET", "retail_demand")
    table = os.getenv("DAILY_SALES_TABLE", "daily_sales")

    conditions = [
        "date IS NOT NULL"
    ]

    parameters = []

    if store_id:
        conditions.append("store_id = @store_id")
        parameters.append(
            bigquery.ScalarQueryParameter(
                "store_id",
                "STRING",
                store_id
            )
        )

    if item_id:
        conditions.append("item_id = @item_id")
        parameters.append(
            bigquery.ScalarQueryParameter(
                "item_id",
                "STRING",
                item_id
            )
        )

    if start_date:
        conditions.append("date >= @start_date")
        parameters.append(
            bigquery.ScalarQueryParameter(
                "start_date",
                "DATE",
                start_date
            )
        )

    if end_date:
        conditions.append("date <= @end_date")
        parameters.append(
            bigquery.ScalarQueryParameter(
                "end_date",
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
        FROM {_table_reference(table, dataset)}
        WHERE {" AND ".join(conditions)}
        ORDER BY date
    """

    return _execute_query(
        query,
        parameters
    )


def get_forecast_metrics(
    model_name: Optional[str] = None
) -> pd.DataFrame:
    """
    Retrieve model evaluation metrics.
    """
    dataset = _get_dataset_name("FORECAST_DATASET", "retail_demand")
    table = os.getenv("METRICS_TABLE", "forecast_metrics")

    conditions = []

    parameters = []

    if model_name:
        conditions.append("model_name = @model_name")
        parameters.append(
            bigquery.ScalarQueryParameter(
                "model_name",
                "STRING",
                model_name
            )
        )

    where_clause = ""

    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    query = f"""
        SELECT
            model_name,
            mae,
            rmse,
            mape,
            r2_score,
            evaluated_at
        FROM {_table_reference(table, dataset)}
        {where_clause}
        ORDER BY mae ASC
    """

    return _execute_query(
        query,
        parameters
    )


def get_model_runs() -> pd.DataFrame:
    """
    Retrieve historical model execution records.
    """
    dataset = _get_dataset_name("FORECAST_DATASET", "retail_demand")
    table = os.getenv("MODEL_RUNS_TABLE", "model_runs")

    query = f"""
        SELECT
            run_id,
            model_name,
            status,
            created_at,
            completed_at
        FROM {_table_reference(table, dataset)}
        ORDER BY created_at DESC
    """

    return _execute_query(query)


import os
from typing import Optional

import pandas as pd
from google.cloud import bigquery


def get_bigquery_client() -> bigquery.Client:
    """Create and return a BigQuery client."""
    project_id = (
        os.getenv("GCP_PROJECT_ID")
        or os.getenv("GOOGLE_CLOUD_PROJECT")
    )

    if not project_id:
        raise ValueError(
            "GCP_PROJECT_ID or GOOGLE_CLOUD_PROJECT "
            "environment variable must be configured."
        )

    return bigquery.Client(project=project_id)


def _get_project_id() -> str:
    project_id = (
        os.getenv("GCP_PROJECT_ID")
        or os.getenv("GOOGLE_CLOUD_PROJECT")
    )

    if not project_id:
        raise ValueError(
            "GCP_PROJECT_ID or GOOGLE_CLOUD_PROJECT "
            "environment variable must be configured."
        )

    return project_id


def _table_reference(
    table_name: str,
    dataset_name: str
) -> str:
    """Build a fully-qualified BigQuery table reference."""
    project_id = _get_project_id()

    return f"`{project_id}.{dataset_name}.{table_name}`"


def _execute_query(
    query: str,
    query_parameters: Optional[list] = None
) -> pd.DataFrame:
    """Execute a parameterized BigQuery query."""
    client = get_bigquery_client()

    job_config = bigquery.QueryJobConfig()

    if query_parameters:
        job_config.query_parameters = query_parameters

    query_job = client.query(
        query,
        job_config=job_config
    )

    return query_job.result().to_dataframe()


def _get_dataset_name(
    environment_variable: str,
    default: str
) -> str:
    return os.getenv(
        environment_variable,
        default
    )


def get_available_stores() -> list:
    """Return distinct store IDs."""
    dataset = _get_dataset_name(
        "FORECAST_DATASET",
        "retail_demand"
    )

    table = os.getenv(
        "FORECAST_TABLE",
        "forecast_results"
    )

    query = f"""
        SELECT DISTINCT store_id
        FROM {_table_reference(table, dataset)}
        WHERE store_id IS NOT NULL
        ORDER BY store_id
    """

    df = _execute_query(query)

    return (
        df["store_id"]
        .dropna()
        .astype(str)
        .tolist()
    )


def get_available_departments() -> list:
    """Return distinct department IDs."""
    dataset = _get_dataset_name(
        "FORECAST_DATASET",
        "retail_demand"
    )

    table = os.getenv(
        "FORECAST_TABLE",
        "forecast_results"
    )

    query = f"""
        SELECT DISTINCT dept_id
        FROM {_table_reference(table, dataset)}
        WHERE dept_id IS NOT NULL
        ORDER BY dept_id
    """

    df = _execute_query(query)

    return (
        df["dept_id"]
        .dropna()
        .astype(str)
        .tolist()
    )


def get_available_categories() -> list:
    """Return distinct category IDs."""
    dataset = _get_dataset_name(
        "FORECAST_DATASET",
        "retail_demand"
    )

    table = os.getenv(
        "FORECAST_TABLE",
        "forecast_results"
    )

    query = f"""
        SELECT DISTINCT cat_id
        FROM {_table_reference(table, dataset)}
        WHERE cat_id IS NOT NULL
        ORDER BY cat_id
    """

    df = _execute_query(query)

    return (
        df["cat_id"]
        .dropna()
        .astype(str)
        .tolist()
    )


def get_available_items(
    store_id: Optional[str] = None,
    dept_id: Optional[str] = None,
    cat_id: Optional[str] = None
) -> list:
    """Return items according to optional filters."""
    dataset = _get_dataset_name(
        "FORECAST_DATASET",
        "retail_demand"
    )

    table = os.getenv(
        "FORECAST_TABLE",
        "forecast_results"
    )

    conditions = [
        "item_id IS NOT NULL"
    ]

    parameters = []

    filters = [
        ("store_id", store_id),
        ("dept_id", dept_id),
        ("cat_id", cat_id),
    ]

    for field, value in filters:
        if value:
            conditions.append(
                f"{field} = @{field}"
            )

            parameters.append(
                bigquery.ScalarQueryParameter(
                    field,
                    "STRING",
                    value
                )
            )

    query = f"""
        SELECT DISTINCT item_id
        FROM {_table_reference(table, dataset)}
        WHERE {" AND ".join(conditions)}
        ORDER BY item_id
    """

    df = _execute_query(
        query,
        parameters
    )

    return (
        df["item_id"]
        .dropna()
        .astype(str)
        .tolist()
    )


def get_available_models() -> list:
    """Return available forecasting models."""
    dataset = _get_dataset_name(
        "FORECAST_DATASET",
        "retail_demand"
    )

    table = os.getenv(
        "FORECAST_TABLE",
        "forecast_results"
    )

    query = f"""
        SELECT DISTINCT model_name
        FROM {_table_reference(table, dataset)}
        WHERE model_name IS NOT NULL
        ORDER BY model_name
    """

    df = _execute_query(query)

    return (
        df["model_name"]
        .dropna()
        .astype(str)
        .tolist()
    )


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
    dataset = _get_dataset_name(
        "FORECAST_DATASET",
        "retail_demand"
    )

    table = os.getenv(
        "FORECAST_TABLE",
        "forecast_results"
    )

    conditions = [
        "forecast_date IS NOT NULL"
    ]

    parameters = []

    filters = [
        ("store_id", store_id),
        ("dept_id", dept_id),
        ("cat_id", cat_id),
        ("item_id", item_id),
        ("model_name", model_name),
    ]

    for field, value in filters:
        if value:
            conditions.append(
                f"{field} = @{field}"
            )

            parameters.append(
                bigquery.ScalarQueryParameter(
                    field,
                    "STRING",
                    value
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
        FROM {_table_reference(table, dataset)}
        WHERE {" AND ".join(conditions)}
        ORDER BY forecast_date
    """

    return _execute_query(
        query,
        parameters
    )


def get_forecast_metrics(
    model_name: Optional[str] = None
) -> pd.DataFrame:
    """Retrieve model evaluation metrics."""
    dataset = _get_dataset_name(
        "FORECAST_DATASET",
        "retail_demand"
    )

    table = os.getenv(
        "METRICS_TABLE",
        "forecast_metrics"
    )

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
                model_name
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
        FROM {_table_reference(table, dataset)}
        {where_clause}
        ORDER BY mae ASC
    """

    return _execute_query(
        query,
        parameters
    )


def get_model_runs() -> pd.DataFrame:
    """Retrieve model execution history."""
    dataset = _get_dataset_name(
        "FORECAST_DATASET",
        "retail_demand"
    )

    table = os.getenv(
        "MODEL_RUNS_TABLE",
        "model_runs"
    )

    query = f"""
        SELECT
            run_id,
            model_name,
            status,
            created_at,
            completed_at
        FROM {_table_reference(table, dataset)}
        ORDER BY created_at DESC
    """

    return _execute_query(query)


def get_latest_forecast_run() -> Optional[str]:
    """Return the latest completed forecast run."""
    dataset = _get_dataset_name(
        "FORECAST_DATASET",
        "retail_demand"
    )

    table = os.getenv(
        "MODEL_RUNS_TABLE",
        "model_runs"
    )

    query = f"""
        SELECT run_id
        FROM {_table_reference(table, dataset)}
        WHERE status = 'completed'
        ORDER BY created_at DESC
        LIMIT 1
    """

    df = _execute_query(query)

    if df.empty:
        return None

    return str(df.iloc[0]["run_id"])


def get_forecast_date_range() -> tuple:
    """Return minimum and maximum forecast dates."""
    dataset = _get_dataset_name(
        "FORECAST_DATASET",
        "retail_demand"
    )

    table = os.getenv(
        "FORECAST_TABLE",
        "forecast_results"
    )

    query = f"""
        SELECT
            MIN(forecast_date) AS min_date,
            MAX(forecast_date) AS max_date
        FROM {_table_reference(table, dataset)}
    """

    df = _execute_query(query)

    if df.empty:
        return None, None

    return (
        df.iloc[0]["min_date"],
        df.iloc[0]["max_date"]
    )


def get_daily_sales(
    store_id: Optional[str] = None,
    item_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> pd.DataFrame:
    """Retrieve historical daily sales."""
    dataset = _get_dataset_name(
        "MARTS_DATASET",
        "retail_demand"
    )

    table = os.getenv(
        "DAILY_SALES_TABLE",
        "daily_sales"
    )

    conditions = [
        "date IS NOT NULL"
    ]

    parameters = []

    if store_id:
        conditions.append(
            "store_id = @store_id"
        )

        parameters.append(
            bigquery.ScalarQueryParameter(
                "store_id",
                "STRING",
                store_id
            )
        )

    if item_id:
        conditions.append(
            "item_id = @item_id"
        )

        parameters.append(
            bigquery.ScalarQueryParameter(
                "item_id",
                "STRING",
                item_id
            )
        )

    if start_date:
        conditions.append(
            "date >= @start_date"
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
            "date <= @end_date"
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
            date,
            store_id,
            item_id,
            dept_id,
            cat_id,
            state_id,
            sales,
            sell_price
        FROM {_table_reference(table, dataset)}
        WHERE {" AND ".join(conditions)}
        ORDER BY date
    """

    return _execute_query(
        query,
        parameters
    )