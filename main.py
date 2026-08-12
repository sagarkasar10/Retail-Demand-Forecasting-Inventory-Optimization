from src.extraction.sales_loader import (
    extract_sales_data,
    validate_sales_columns,
    prepare_sales_for_bigquery,
    print_sales_summary,
)

from src.extraction.calendar_loader import (
    extract_calendar_data,
    validate_calendar_columns,
    prepare_calendar_for_bigquery,
    print_calendar_summary,
)

from src.extraction.prices_loader import (
    extract_prices_data,
    validate_prices_columns,
    prepare_prices_for_bigquery,
    print_prices_summary,
)

from src.validation.schema_checks import (
    validate_dataset_schema,
)

from src.warehouse.bigquery_client import (
    get_bigquery_client,
    create_dataset_if_not_exists,
    load_dataframe_to_bigquery,
    get_table_row_count,
)


# ============================================================
# CONFIGURATION
# ============================================================

SALES_PATH = "data/raw/sales_train_validation.csv"
CALENDAR_PATH = "data/raw/calendar.csv"
PRICES_PATH = "data/raw/sell_prices.csv"

BIGQUERY_DATASET = "retail_demand"

SALES_TABLE = "raw_sales"
CALENDAR_TABLE = "raw_calendar"
PRICES_TABLE = "raw_prices"


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():
    """
    Execute the Week 1 Day 3 ETL pipeline.
    """

    print("\n")
    print("=" * 70)
    print("RETAIL DEMAND FORECASTING & INVENTORY OPTIMIZATION")
    print("WEEK 1 - DAY 3 ETL PIPELINE")
    print("=" * 70)

    # --------------------------------------------------------
    # STEP 1: BigQuery connection
    # --------------------------------------------------------

    print("\n[1/7] INITIALIZING BIGQUERY")

    client = get_bigquery_client(
        project_id=None
    )

    create_dataset_if_not_exists(
        client=client,
        dataset_name=BIGQUERY_DATASET,
        location="US"
    )

    # --------------------------------------------------------
    # STEP 2: Extract sales
    # --------------------------------------------------------

    print("\n[2/7] EXTRACTING SALES DATA")

    sales_df = extract_sales_data(
        SALES_PATH
    )

    validate_sales_columns(
        sales_df
    )

    print_sales_summary(
        sales_df
    )

    # --------------------------------------------------------
    # STEP 3: Extract calendar
    # --------------------------------------------------------

    print("\n[3/7] EXTRACTING CALENDAR DATA")

    calendar_df = extract_calendar_data(
        CALENDAR_PATH
    )

    validate_calendar_columns(
        calendar_df
    )

    print_calendar_summary(
        calendar_df
    )

    # --------------------------------------------------------
    # STEP 4: Extract prices
    # --------------------------------------------------------

    print("\n[4/7] EXTRACTING PRICING DATA")

    prices_df = extract_prices_data(
        PRICES_PATH
    )

    validate_prices_columns(
        prices_df
    )

    print_prices_summary(
        prices_df
    )

    # --------------------------------------------------------
    # STEP 5: Prepare data
    # --------------------------------------------------------

    print("\n[5/7] PREPARING DATA FOR BIGQUERY")

    sales_df = prepare_sales_for_bigquery(
        sales_df
    )

    calendar_df = prepare_calendar_for_bigquery(
        calendar_df
    )

    prices_df = prepare_prices_for_bigquery(
        prices_df
    )

    # --------------------------------------------------------
    # STEP 6: Common schema validation
    # --------------------------------------------------------

    print("\n[6/7] RUNNING SCHEMA VALIDATION")

    validate_dataset_schema(
        sales_df,
        [
            "id",
            "item_id",
            "dept_id",
            "cat_id",
            "store_id",
            "state_id",
        ],
        "Sales"
    )

    validate_dataset_schema(
        calendar_df,
        [
            "date",
            "wm_yr_wk",
            "weekday",
            "wday",
            "month",
            "year",
        ],
        "Calendar"
    )

    validate_dataset_schema(
        prices_df,
        [
            "store_id",
            "item_id",
            "wm_yr_wk",
            "sell_price",
        ],
        "Prices"
    )

    # --------------------------------------------------------
    # STEP 7: Load data into BigQuery
    # --------------------------------------------------------

    print("\n[7/7] LOADING DATA INTO BIGQUERY")

    load_dataframe_to_bigquery(
        client=client,
        dataframe=sales_df,
        dataset_name=BIGQUERY_DATASET,
        table_name=SALES_TABLE,
        write_disposition="WRITE_TRUNCATE"
    )

    load_dataframe_to_bigquery(
        client=client,
        dataframe=calendar_df,
        dataset_name=BIGQUERY_DATASET,
        table_name=CALENDAR_TABLE,
        write_disposition="WRITE_TRUNCATE"
    )

    load_dataframe_to_bigquery(
        client=client,
        dataframe=prices_df,
        dataset_name=BIGQUERY_DATASET,
        table_name=PRICES_TABLE,
        write_disposition="WRITE_TRUNCATE"
    )

    # --------------------------------------------------------
    # VERIFY LOADED ROW COUNTS
    # --------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("BIGQUERY LOAD VERIFICATION")
    print("=" * 70)

    sales_count = get_table_row_count(
        client,
        BIGQUERY_DATASET,
        SALES_TABLE
    )

    calendar_count = get_table_row_count(
        client,
        BIGQUERY_DATASET,
        CALENDAR_TABLE
    )

    prices_count = get_table_row_count(
        client,
        BIGQUERY_DATASET,
        PRICES_TABLE
    )

    print(
        f"raw_sales    : {sales_count:,} rows"
    )

    print(
        f"raw_calendar : {calendar_count:,} rows"
    )

    print(
        f"raw_prices   : {prices_count:,} rows"
    )


if __name__ == "__main__":
    main()