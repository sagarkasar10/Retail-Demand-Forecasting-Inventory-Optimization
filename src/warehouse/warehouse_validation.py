from google.cloud import bigquery


def check_table_exists(
    client: bigquery.Client,
    project_id: str,
    dataset_name: str,
    table_name: str
) -> bool:
    """
    Check whether a BigQuery table exists.
    """

    table_id = f"{project_id}.{dataset_name}.{table_name}"

    try:
        client.get_table(table_id)

        print(f"✓ Table exists: {table_name}")

        return True

    except Exception as error:

        print(f"✗ Table does not exist: {table_name}")
        print(f"Error: {error}")

        return False


def get_table_row_count(
    client: bigquery.Client,
    project_id: str,
    dataset_name: str,
    table_name: str
) -> int:
    """
    Return the number of rows in a BigQuery table.
    """

    query = f"""
        SELECT COUNT(*) AS row_count
        FROM `{project_id}.{dataset_name}.{table_name}`
    """

    result = client.query(query).result()

    row = next(iter(result))

    return int(row.row_count)


def verify_week1_tables(
    client: bigquery.Client,
    project_id: str,
    dataset_name: str
) -> bool:
    """
    Verify all raw and clean Week 1 BigQuery tables.
    """

    tables = [
        "raw_sales",
        "raw_calendar",
        "raw_prices",
        "clean_sales",
        "clean_calendar",
        "clean_prices",
    ]

    print("\n")
    print("=" * 60)
    print("BIGQUERY WEEK 1 TABLE VERIFICATION")
    print("=" * 60)

    all_valid = True

    for table_name in tables:

        # Check whether table exists
        exists = check_table_exists(
            client,
            project_id,
            dataset_name,
            table_name
        )

        if not exists:
            all_valid = False
            continue

        # Check row count
        row_count = get_table_row_count(
            client,
            project_id,
            dataset_name,
            table_name
        )

        print(f"  Rows: {row_count:,}")

        # Check whether table contains data
        if row_count == 0:

            print(f"✗ Table is empty: {table_name}")

            all_valid = False

        else:

            print("✓ Table contains data")

    print("=" * 60)

    if all_valid:

        print("✓ ALL BIGQUERY TABLES VERIFIED")

    else:

        print("✗ BIGQUERY VERIFICATION FAILED")

    return all_valid