from google.cloud import bigquery


def create_clean_sales_table(
    client,
    project_id: str,
    dataset_name: str
):
    """
    Create the clean_sales table from raw_sales.

    The M5 sales dataset is kept in wide format during Week 1.
    Daily columns such as d_1, d_2, ... remain unchanged.
    """

    query = f"""
    CREATE OR REPLACE TABLE
    `{project_id}.{dataset_name}.clean_sales`
    AS

    SELECT
        CAST(id AS STRING) AS id,
        CAST(item_id AS STRING) AS item_id,
        CAST(dept_id AS STRING) AS dept_id,
        CAST(cat_id AS STRING) AS cat_id,
        CAST(store_id AS STRING) AS store_id,
        CAST(state_id AS STRING) AS state_id,

        * EXCEPT(
            id,
            item_id,
            dept_id,
            cat_id,
            store_id,
            state_id
        )

    FROM `{project_id}.{dataset_name}.raw_sales`
    """

    try:
        job = client.query(query)
        job.result()

        print(
            f"✓ clean_sales table created: "
            f"{project_id}.{dataset_name}.clean_sales"
        )

    except Exception as exc:
        raise RuntimeError(
            f"Failed to create clean_sales: {exc}"
        ) from exc


def create_clean_calendar_table(
    client,
    project_id: str,
    dataset_name: str
):
    """
    Create a standardized calendar table.
    """

    query = f"""
    CREATE OR REPLACE TABLE
    `{project_id}.{dataset_name}.clean_calendar`
    AS

    SELECT
        SAFE_CAST(date AS DATE) AS date,
        SAFE_CAST(wm_yr_wk AS INT64) AS wm_yr_wk,
        CAST(weekday AS STRING) AS weekday,
        SAFE_CAST(wday AS INT64) AS wday,
        SAFE_CAST(month AS INT64) AS month,
        SAFE_CAST(year AS INT64) AS year,

        CAST(event_name_1 AS STRING) AS event_name_1,
        CAST(event_type_1 AS STRING) AS event_type_1,
        CAST(event_name_2 AS STRING) AS event_name_2,
        CAST(event_type_2 AS STRING) AS event_type_2,

        SAFE_CAST(snap_CA AS INT64) AS snap_CA,
        SAFE_CAST(snap_TX AS INT64) AS snap_TX,
        SAFE_CAST(snap_WI AS INT64) AS snap_WI

    FROM `{project_id}.{dataset_name}.raw_calendar`
    """

    try:
        job = client.query(query)
        job.result()

        print(
            f"✓ clean_calendar table created: "
            f"{project_id}.{dataset_name}.clean_calendar"
        )

    except Exception as exc:
        raise RuntimeError(
            f"Failed to create clean_calendar: {exc}"
        ) from exc


def create_clean_prices_table(
    client,
    project_id: str,
    dataset_name: str
):
    """
    Create a standardized pricing table.
    """

    query = f"""
    CREATE OR REPLACE TABLE
    `{project_id}.{dataset_name}.clean_prices`
    AS

    SELECT
        CAST(store_id AS STRING) AS store_id,
        CAST(item_id AS STRING) AS item_id,
        SAFE_CAST(wm_yr_wk AS INT64) AS wm_yr_wk,
        SAFE_CAST(sell_price AS FLOAT64) AS sell_price

    FROM `{project_id}.{dataset_name}.raw_prices`

    WHERE sell_price IS NULL
       OR sell_price >= 0
    """

    try:
        job = client.query(query)
        job.result()

        print(
            f"✓ clean_prices table created: "
            f"{project_id}.{dataset_name}.clean_prices"
        )

    except Exception as exc:
        raise RuntimeError(
            f"Failed to create clean_prices: {exc}"
        ) from exc


def create_all_clean_tables(
    client,
    project_id: str,
    dataset_name: str
):
    """
    Create all Week-1 clean tables.
    """

    print("\nCreating clean BigQuery tables...")

    create_clean_sales_table(
        client,
        project_id,
        dataset_name
    )

    create_clean_calendar_table(
        client,
        project_id,
        dataset_name
    )

    create_clean_prices_table(
        client,
        project_id,
        dataset_name
    )

    print(
        "\n✓ All clean tables created successfully."
    )