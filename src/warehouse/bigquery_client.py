import os

from google.cloud import bigquery
from dotenv import load_dotenv


# Load variables from .env
load_dotenv()


def get_bigquery_client():
    """
    Create and return a BigQuery client.

    The Google Cloud project ID is read from the
    GOOGLE_CLOUD_PROJECT environment variable.
    """

    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")

    if not project_id:
        raise ValueError(
            "GOOGLE_CLOUD_PROJECT is not configured in the .env file."
        )

    try:
        client = bigquery.Client(project=project_id)

        print(f"✓ BigQuery client created for project: {project_id}")

        return client

    except Exception as exc:
        raise RuntimeError(
            f"Failed to create BigQuery client: {exc}"
        ) from exc


def create_dataset_if_not_exists(
    client,
    dataset_name: str,
    location: str = "US"
):
    """
    Create the BigQuery dataset if it does not already exist.
    """

    dataset_id = f"{client.project}.{dataset_name}"

    dataset = bigquery.Dataset(dataset_id)
    dataset.location = location

    try:
        client.create_dataset(
            dataset,
            exists_ok=True
        )

        print(
            f"✓ BigQuery dataset is ready: {dataset_id}"
        )

        return dataset_id

    except Exception as exc:
        raise RuntimeError(
            f"Failed to create/check BigQuery dataset "
            f"{dataset_id}: {exc}"
        ) from exc


def table_exists(
    client,
    dataset_name: str,
    table_name: str
) -> bool:
    """
    Check whether a BigQuery table exists.
    """

    table_id = (
        f"{client.project}."
        f"{dataset_name}."
        f"{table_name}"
    )

    try:
        client.get_table(table_id)

        print(f"✓ Table exists: {table_id}")

        return True

    except Exception:
        print(f"Table does not exist: {table_id}")

        return False

def load_dataframe_to_bigquery(
    client,
    dataframe,
    dataset_name: str,
    table_name: str,
    write_disposition: str = "WRITE_TRUNCATE"
):
    """
    Load a pandas DataFrame into a BigQuery table.

    WRITE_TRUNCATE:
        Replace the table if it already exists.

    WRITE_APPEND:
        Add records to an existing table.
    """

    if dataframe is None:
        raise ValueError(
            f"Cannot load None DataFrame into {table_name}."
        )

    if dataframe.empty:
        raise ValueError(
            f"Cannot load empty DataFrame into {table_name}."
        )

    table_id = (
        f"{client.project}."
        f"{dataset_name}."
        f"{table_name}"
    )

    job_config = bigquery.LoadJobConfig(
        write_disposition=write_disposition
    )

    print(
        f"Loading {len(dataframe):,} rows "
        f"into {table_id}..."
    )

    try:
        load_job = client.load_table_from_dataframe(
            dataframe,
            table_id,
            job_config=job_config
        )

        load_job.result()

        table = client.get_table(table_id)

        print(
            f"✓ Successfully loaded "
            f"{table.num_rows:,} rows into {table_id}"
        )

        return table

    except Exception as exc:
        raise RuntimeError(
            f"Failed to load DataFrame into "
            f"{table_id}: {exc}"
        ) from exc


def get_table_row_count(
    client,
    dataset_name: str,
    table_name: str
) -> int:
    """
    Return the number of rows in a BigQuery table.
    """

    table_id = (
        f"{client.project}."
        f"{dataset_name}."
        f"{table_name}"
    )

    try:
        table = client.get_table(table_id)

        return table.num_rows

    except Exception as exc:
        raise RuntimeError(
            f"Failed to get row count for "
            f"{table_id}: {exc}"
        ) from exc
    

