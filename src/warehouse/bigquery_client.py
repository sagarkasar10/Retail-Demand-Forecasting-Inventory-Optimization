import os

from google.cloud import bigquery
from dotenv import load_dotenv


# Load variables from .env
load_dotenv()


def get_bigquery_client():
    """
    Create and return an authenticated BigQuery client.
    """

    project_id = (
        os.getenv("GCP_PROJECT_ID")
        or os.getenv("GOOGLE_CLOUD_PROJECT")
    )

    credentials_path = os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS"
    )

    if not project_id:
        raise ValueError(
            "BigQuery project ID is missing. "
            "Set GCP_PROJECT_ID or GOOGLE_CLOUD_PROJECT in .env."
        )

    if credentials_path:

        if not os.path.exists(credentials_path):
            raise FileNotFoundError(
                "Google service account credentials file was not found: "
                f"{credentials_path}"
            )

        print(
            "✓ Google credentials file found: "
            f"{credentials_path}"
        )

    else:
        print(
            "⚠ GOOGLE_APPLICATION_CREDENTIALS is not set. "
            "Trying Application Default Credentials."
        )

    try:

        client = bigquery.Client(
            project=project_id
        )

        print(
            f"✓ BigQuery client created successfully "
            f"for project: {client.project}"
        )

        return client

    except Exception as exc:

        raise RuntimeError(
            "Failed to authenticate with Google BigQuery. "
            f"Original error: {exc}"
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
    

