from __future__ import annotations

import os
from typing import Optional

import pandas as pd
from google.cloud import bigquery


DEFAULT_DATASET = "retail_demand_forecasting"
DEFAULT_FORECAST_TABLE = "forecast_predictions"
DEFAULT_METRICS_TABLE = "forecast_metrics"
DEFAULT_RUNS_TABLE = "model_runs"


FORECAST_SCHEMA = [
    bigquery.SchemaField(
        "forecast_date",
        "DATE",
        mode="REQUIRED",
    ),
    bigquery.SchemaField(
        "item_id",
        "STRING",
        mode="NULLABLE",
    ),
    bigquery.SchemaField(
        "store_id",
        "STRING",
        mode="NULLABLE",
    ),
    bigquery.SchemaField(
        "dept_id",
        "STRING",
        mode="NULLABLE",
    ),
    bigquery.SchemaField(
        "cat_id",
        "STRING",
        mode="NULLABLE",
    ),
    bigquery.SchemaField(
        "model_name",
        "STRING",
        mode="REQUIRED",
    ),
    bigquery.SchemaField(
        "predicted_demand",
        "FLOAT64",
        mode="REQUIRED",
    ),
    bigquery.SchemaField(
        "prediction_lower",
        "FLOAT64",
        mode="NULLABLE",
    ),
    bigquery.SchemaField(
        "prediction_upper",
        "FLOAT64",
        mode="NULLABLE",
    ),
    bigquery.SchemaField(
        "forecast_created_at",
        "TIMESTAMP",
        mode="REQUIRED",
    ),
]


METRICS_SCHEMA = [
    bigquery.SchemaField(
        "model_name",
        "STRING",
        mode="REQUIRED",
    ),
    bigquery.SchemaField(
        "mae",
        "FLOAT64",
        mode="NULLABLE",
    ),
    bigquery.SchemaField(
        "rmse",
        "FLOAT64",
        mode="NULLABLE",
    ),
    bigquery.SchemaField(
        "mape",
        "FLOAT64",
        mode="NULLABLE",
    ),
    bigquery.SchemaField(
        "wape",
        "FLOAT64",
        mode="NULLABLE",
    ),
    bigquery.SchemaField(
        "bias",
        "FLOAT64",
        mode="NULLABLE",
    ),
    bigquery.SchemaField(
        "rows_evaluated",
        "INT64",
        mode="NULLABLE",
    ),
    bigquery.SchemaField(
        "evaluation_date",
        "TIMESTAMP",
        mode="REQUIRED",
    ),
]


RUN_SCHEMA = [
    bigquery.SchemaField(
        "run_id",
        "STRING",
        mode="REQUIRED",
    ),
    bigquery.SchemaField(
        "model_name",
        "STRING",
        mode="REQUIRED",
    ),
    bigquery.SchemaField(
        "run_type",
        "STRING",
        mode="REQUIRED",
    ),
    bigquery.SchemaField(
        "start_date",
        "DATE",
        mode="NULLABLE",
    ),
    bigquery.SchemaField(
        "end_date",
        "DATE",
        mode="NULLABLE",
    ),
    bigquery.SchemaField(
        "forecast_horizon",
        "INT64",
        mode="NULLABLE",
    ),
    bigquery.SchemaField(
        "status",
        "STRING",
        mode="REQUIRED",
    ),
    bigquery.SchemaField(
        "created_at",
        "TIMESTAMP",
        mode="REQUIRED",
    ),
]


def get_bigquery_client(
    project_id: Optional[str] = None,
) -> bigquery.Client:
    """Create a BigQuery client."""

    project_id = os.environ.get("GCP_PROJECT_ID") or os.environ["GOOGLE_CLOUD_PROJECT"]

    if not project_id:
        return bigquery.Client()

    return bigquery.Client(
        project=project_id
    )


def ensure_dataset(
    client: bigquery.Client,
    project_id: str,
    dataset_id: str,
) -> None:
    """Create the forecasting dataset when it does not exist."""

    dataset_ref = f"{project_id}.{dataset_id}"

    dataset = bigquery.Dataset(
        dataset_ref
    )

    dataset.location = os.getenv(
        "BIGQUERY_LOCATION",
        "US",
    )

    client.create_dataset(
        dataset,
        exists_ok=True,
    )


def write_forecasts(
    forecast_df: pd.DataFrame,
    table_name: str = DEFAULT_FORECAST_TABLE,
    project_id: Optional[str] = None,
    dataset_id: Optional[str] = None,
    write_disposition: str = "WRITE_APPEND",
) -> int:
    """Write forecast predictions to BigQuery."""

    if forecast_df.empty:
        raise ValueError(
            "Forecast dataframe cannot be empty."
        )

    project_id = project_id or os.environ.get("GCP_PROJECT_ID") or os.environ["GOOGLE_CLOUD_PROJECT"]

    dataset_id = dataset_id or os.getenv(
        "BIGQUERY_FORECAST_DATASET",
        DEFAULT_DATASET,
    )

    if not project_id:
        raise ValueError(
            "GCP_PROJECT_ID environment variable is required."
        )

    required_columns = {
        "forecast_date",
        "model_name",
        "predicted_demand",
    }

    missing = required_columns - set(
        forecast_df.columns
    )

    if missing:
        raise ValueError(
            f"Missing forecast columns: {sorted(missing)}"
        )

    output = forecast_df.copy()

    output["forecast_date"] = pd.to_datetime(
        output["forecast_date"],
        errors="coerce",
    ).dt.date

    output["predicted_demand"] = pd.to_numeric(
        output["predicted_demand"],
        errors="coerce",
    )

    output["forecast_created_at"] = pd.to_datetime(
        output.get(
            "forecast_created_at",
            pd.Timestamp.utcnow(),
        ),
        errors="coerce",
    )

    output["forecast_created_at"] = (
        output["forecast_created_at"]
        .fillna(pd.Timestamp.utcnow())
    )

    if "prediction_lower" not in output.columns:
        output["prediction_lower"] = None

    if "prediction_upper" not in output.columns:
        output["prediction_upper"] = None

    for column in [
        "item_id",
        "store_id",
        "dept_id",
        "cat_id",
    ]:
        if column not in output.columns:
            output[column] = None

    output = output[
        [
            "forecast_date",
            "item_id",
            "store_id",
            "dept_id",
            "cat_id",
            "model_name",
            "predicted_demand",
            "prediction_lower",
            "prediction_upper",
            "forecast_created_at",
        ]
    ]

    if output["forecast_date"].isna().any():
        raise ValueError(
            "Forecast output contains invalid dates."
        )

    if output["predicted_demand"].isna().any():
        raise ValueError(
            "Forecast output contains invalid predictions."
        )

    if (
        output["predicted_demand"] < 0
    ).any():
        raise ValueError(
            "Forecast output contains negative predictions."
        )

    client = get_bigquery_client(
        project_id
    )

    ensure_dataset(
        client,
        project_id,
        dataset_id,
    )

    table_ref = (
        f"{project_id}.{dataset_id}.{table_name}"
    )

    job_config = bigquery.LoadJobConfig(
        schema=FORECAST_SCHEMA,
        write_disposition=write_disposition,
    )

    job = client.load_table_from_dataframe(
        output,
        table_ref,
        job_config=job_config,
    )

    job.result()

    return len(output)


def write_metrics(
    metrics: list[dict] | pd.DataFrame,
    table_name: str = DEFAULT_METRICS_TABLE,
    project_id: Optional[str] = None,
    dataset_id: Optional[str] = None,
) -> int:
    """Write model evaluation metrics to BigQuery."""

    if isinstance(metrics, list):
        dataframe = pd.DataFrame(metrics)
    else:
        dataframe = metrics.copy()

    if dataframe.empty:
        raise ValueError(
            "Metrics dataframe cannot be empty."
        )

    project_id = project_id or os.environ.get("GCP_PROJECT_ID") or os.environ["GOOGLE_CLOUD_PROJECT"]

    dataset_id = dataset_id or os.environ.get(
        "BIGQUERY_FORECAST_DATASET",
        DEFAULT_DATASET,
    )

    if not project_id:
        raise ValueError(
            "GCP_PROJECT_ID environment variable is required."
        )

    required = {
        "model_name",
        "mae",
        "rmse",
        "mape",
        "wape",
    }

    missing = required - set(
        dataframe.columns
    )

    if missing:
        raise ValueError(
            f"Missing metric columns: {sorted(missing)}"
        )

    dataframe = dataframe.copy()

    if "bias" not in dataframe.columns:
        dataframe["bias"] = None

    if "rows_evaluated" not in dataframe.columns:
        dataframe["rows_evaluated"] = None

    dataframe["evaluation_date"] = pd.Timestamp.utcnow()

    dataframe = dataframe[
        [
            "model_name",
            "mae",
            "rmse",
            "mape",
            "wape",
            "bias",
            "rows_evaluated",
            "evaluation_date",
        ]
    ]

    client = get_bigquery_client(
        project_id
    )

    ensure_dataset(
        client,
        project_id,
        dataset_id,
    )

    table_ref = (
        f"{project_id}.{dataset_id}.{table_name}"
    )

    job_config = bigquery.LoadJobConfig(
        schema=METRICS_SCHEMA,
        write_disposition="WRITE_APPEND",
    )

    job = client.load_table_from_dataframe(
        dataframe,
        table_ref,
        job_config=job_config,
    )

    job.result()

    return len(dataframe)


def write_model_run(
    run_id: str,
    model_name: str,
    run_type: str,
    status: str,
    start_date=None,
    end_date=None,
    forecast_horizon: Optional[int] = None,
    table_name: str = DEFAULT_RUNS_TABLE,
    project_id: Optional[str] = None,
    dataset_id: Optional[str] = None,
) -> int:
    """Write a model execution record to BigQuery."""

    if not run_id:
        raise ValueError(
            "run_id is required."
        )

    if not model_name:
        raise ValueError(
            "model_name is required."
        )

    if not run_type:
        raise ValueError(
            "run_type is required."
        )

    if not status:
        raise ValueError(
            "status is required."
        )

    project_id = os.environ.get("GCP_PROJECT_ID") or os.environ["GOOGLE_CLOUD_PROJECT"]

    dataset_id = dataset_id or os.environ.get(
        "BIGQUERY_FORECAST_DATASET",
        DEFAULT_DATASET,
    )

    if not project_id:
        raise ValueError(
            "GCP_PROJECT_ID environment variable is required."
        )

    dataframe = pd.DataFrame(
        [
            {
                "run_id": run_id,
                "model_name": model_name,
                "run_type": run_type,
                "start_date": start_date,
                "end_date": end_date,
                "forecast_horizon": forecast_horizon,
                "status": status,
                "created_at": pd.Timestamp.utcnow(),
            }
        ]
    )

    dataframe["start_date"] = pd.to_datetime(
        dataframe["start_date"],
        errors="coerce",
    ).dt.date

    dataframe["end_date"] = pd.to_datetime(
        dataframe["end_date"],
        errors="coerce",
    ).dt.date

    client = get_bigquery_client(
        project_id
    )

    ensure_dataset(
        client,
        project_id,
        dataset_id,
    )

    table_ref = (
        f"{project_id}.{dataset_id}.{table_name}"
    )

    job_config = bigquery.LoadJobConfig(
        schema=RUN_SCHEMA,
        write_disposition="WRITE_APPEND",
    )

    job = client.load_table_from_dataframe(
        dataframe,
        table_ref,
        job_config=job_config,
    )

    job.result()

    return 1
