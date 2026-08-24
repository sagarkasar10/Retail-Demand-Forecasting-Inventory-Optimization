from google.cloud import bigquery


def run_query(client, query: str):
    """
    Execute a BigQuery SQL query and return the result.
    """
    try:
        query_job = client.query(query)
        result = query_job.result()
        return result

    except Exception as exc:
        raise RuntimeError(
            f"BigQuery query failed: {exc}"
        ) from exc


def check_table_exists(
    client,
    project_id: str,
    dataset_name: str,
    table_name: str
) -> bool:
    """
    Check whether a BigQuery table exists.
    """
    table_id = (
        f"{project_id}."
        f"{dataset_name}."
        f"{table_name}"
    )

    try:
        client.get_table(table_id)

        print(f"✓ Table exists: {table_id}")
        return True

    except Exception:
        print(f"✗ Table does not exist: {table_id}")
        return False


def check_row_count(
    client,
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

    result = run_query(client, query)
    row = next(iter(result))

    row_count = row.row_count

    print(
        f"✓ {table_name}: "
        f"{row_count:,} rows"
    )

    return row_count


def check_null_counts(
    client,
    project_id: str,
    dataset_name: str,
    table_name: str,
    columns: list[str]
) -> dict:
    """
    Check NULL values for selected columns.
    """
    expressions = []

    for column in columns:
        expressions.append(
            f"COUNTIF({column} IS NULL) AS {column}_null_count"
        )

    query = f"""
        SELECT
            {", ".join(expressions)}
        FROM `{project_id}.{dataset_name}.{table_name}`
    """

    result = run_query(client, query)
    row = next(iter(result))

    null_counts = {}

    for column in columns:
        count = getattr(
            row,
            f"{column}_null_count"
        )

        null_counts[column] = count

        if count == 0:
            print(
                f"✓ {table_name}.{column}: "
                f"no NULL values"
            )
        else:
            print(
                f"⚠ {table_name}.{column}: "
                f"{count:,} NULL values"
            )

    return null_counts


def check_negative_prices(
    client,
    project_id: str,
    dataset_name: str,
    table_name: str = "raw_prices"
) -> int:
    """
    Check for negative selling prices.
    """
    query = f"""
        SELECT COUNT(*) AS negative_count
        FROM `{project_id}.{dataset_name}.{table_name}`
        WHERE sell_price < 0
    """

    result = run_query(client, query)
    row = next(iter(result))

    count = row.negative_count

    if count == 0:
        print("✓ No negative prices found")
    else:
        print(
            f"⚠ Found {count:,} negative prices"
        )

    return count


def check_duplicate_prices(
    client,
    project_id: str,
    dataset_name: str,
    table_name: str = "raw_prices"
) -> int:
    """
    Check duplicate store/item/week combinations.
    """
    query = f"""
        SELECT COUNT(*) AS duplicate_groups
        FROM (
            SELECT
                store_id,
                item_id,
                wm_yr_wk,
                COUNT(*) AS record_count
            FROM `{project_id}.{dataset_name}.{table_name}`
            GROUP BY
                store_id,
                item_id,
                wm_yr_wk
            HAVING COUNT(*) > 1
        )
    """

    result = run_query(client, query)
    row = next(iter(result))

    count = row.duplicate_groups

    if count == 0:
        print("✓ No duplicate price keys found")
    else:
        print(
            f"⚠ Found {count:,} duplicate price groups"
        )

    return count


def check_calendar_dates(
    client,
    project_id: str,
    dataset_name: str,
    table_name: str = "raw_calendar"
) -> dict:
    """
    Check calendar date range and duplicate dates.
    """
    query = f"""
        SELECT
            MIN(date) AS minimum_date,
            MAX(date) AS maximum_date,
            COUNT(DISTINCT date) AS unique_dates,
            COUNT(*) AS total_rows
        FROM `{project_id}.{dataset_name}.{table_name}`
    """

    result = run_query(client, query)
    row = next(iter(result))

    output = {
        "minimum_date": row.minimum_date,
        "maximum_date": row.maximum_date,
        "unique_dates": row.unique_dates,
        "total_rows": row.total_rows,
    }

    print(
        f"✓ Calendar range: "
        f"{output['minimum_date']} → "
        f"{output['maximum_date']}"
    )

    return output


def run_all_quality_checks(
    client,
    project_id: str,
    dataset_name: str,
    include_clean: bool = False,
) -> bool:
    """
    Run Week 1 BigQuery quality checks.
    """

    print("\n" + "=" * 60)
    print("BIGQUERY DATA QUALITY CHECKS")
    print("=" * 60)

    tables = [
        "raw_sales",
        "raw_calendar",
        "raw_prices",
    ]

    if include_clean:
        tables.extend([
            "clean_sales",
            "clean_calendar",
            "clean_prices",
        ])

    all_passed = True

    for table in tables:

        exists = check_table_exists(
            client,
            project_id,
            dataset_name,
            table,
        )

        if not exists:
            all_passed = False
            continue

        row_count = check_row_count(
            client,
            project_id,
            dataset_name,
            table,
        )

        if row_count == 0:
            all_passed = False

    check_null_counts(
        client,
        project_id,
        dataset_name,
        "raw_sales",
        [
            "id",
            "item_id",
            "dept_id",
            "cat_id",
            "store_id",
            "state_id",
        ],
    )

    check_null_counts(
        client,
        project_id,
        dataset_name,
        "raw_calendar",
        [
            "date",
            "wm_yr_wk",
        ],
    )

    check_null_counts(
        client,
        project_id,
        dataset_name,
        "raw_prices",
        [
            "store_id",
            "item_id",
            "wm_yr_wk",
            "sell_price",
        ],
    )

    negative_prices = check_negative_prices(
        client,
        project_id,
        dataset_name,
    )

    duplicate_prices = check_duplicate_prices(
        client,
        project_id,
        dataset_name,
    )

    check_calendar_dates(
        client,
        project_id,
        dataset_name,
    )

    if negative_prices > 0:
        all_passed = False

    if duplicate_prices > 0:
        all_passed = False

    print("=" * 60)

    if all_passed:
        print("✓ BIGQUERY QUALITY CHECKS PASSED")
    else:
        print("✗ BIGQUERY QUALITY CHECKS FAILED")

    print("=" * 60)

    return all_passed