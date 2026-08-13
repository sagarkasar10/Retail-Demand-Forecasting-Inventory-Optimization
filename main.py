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

from src.validation.sales_quality import (
    check_sales_values,
    clean_sales_data,
)

from src.validation.calendar_quality import (
    validate_calendar_dates,
    clean_calendar_data,
)

from src.validation.pricing_quality import (
    validate_pricing_data,
    clean_pricing_data,
)

from src.validation.bigquery_quality import (
    run_all_quality_checks,
)

from src.warehouse.bigquery_client import (
    get_bigquery_client,
    create_dataset_if_not_exists,
    load_dataframe_to_bigquery,
)


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ID = "GCP_PROJECT_ID"  

BIGQUERY_DATASET = "retail_demand"

SALES_PATH = (
    "data/raw/sales_train_validation.csv"
)

CALENDAR_PATH = (
    "data/raw/calendar.csv"
)

PRICES_PATH = (
    "data/raw/sell_prices.csv"
)


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")
    print("=" * 70)
    print(
        "RETAIL DEMAND FORECASTING & "
        "INVENTORY OPTIMIZATION"
    )
    print("WEEK 1 - DAY 4")
    print("=" * 70)

    # --------------------------------------------------------
    # 1. BIGQUERY CONNECTION
    # --------------------------------------------------------

    print("\n[1/8] INITIALIZING BIGQUERY")

    client = get_bigquery_client(
        project_id=PROJECT_ID
    )

    create_dataset_if_not_exists(
        client,
        BIGQUERY_DATASET
    )

    # --------------------------------------------------------
    # 2. EXTRACT SALES
    # --------------------------------------------------------

    print("\n[2/8] EXTRACTING SALES")

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
    # 3. SALES QUALITY + CLEANING
    # --------------------------------------------------------

    print("\n[3/8] VALIDATING SALES DATA")

    check_sales_values(
        sales_df
    )

    sales_df = clean_sales_data(
        sales_df
    )

    # --------------------------------------------------------
    # 4. CALENDAR
    # --------------------------------------------------------

    print("\n[4/8] VALIDATING CALENDAR DATA")

    calendar_df = extract_calendar_data(
        CALENDAR_PATH
    )

    validate_calendar_columns(
        calendar_df
    )

    validate_calendar_dates(
        calendar_df
    )

    calendar_df = clean_calendar_data(
        calendar_df
    )

    # --------------------------------------------------------
    # 5. PRICING
    # --------------------------------------------------------

    print("\n[5/8] VALIDATING PRICING DATA")

    prices_df = extract_prices_data(
        PRICES_PATH
    )

    validate_prices_columns(
        prices_df
    )

    validate_pricing_data(
        prices_df
    )

    prices_df = clean_pricing_data(
        prices_df
    )

    # --------------------------------------------------------
    # 6. PREPARE DATA
    # --------------------------------------------------------

    print("\n[6/8] PREPARING DATA")

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
    # 7. LOAD CLEANED DATA
    # --------------------------------------------------------

    print("\n[7/8] LOADING CLEANED DATA")

    load_dataframe_to_bigquery(
        client=client,
        dataframe=sales_df,
        dataset_name=BIGQUERY_DATASET,
        table_name="raw_sales",
        write_disposition="WRITE_TRUNCATE"
    )

    load_dataframe_to_bigquery(
        client=client,
        dataframe=calendar_df,
        dataset_name=BIGQUERY_DATASET,
        table_name="raw_calendar",
        write_disposition="WRITE_TRUNCATE"
    )

    load_dataframe_to_bigquery(
        client=client,
        dataframe=prices_df,
        dataset_name=BIGQUERY_DATASET,
        table_name="raw_prices",
        write_disposition="WRITE_TRUNCATE"
    )

    # --------------------------------------------------------
    # 8. BIGQUERY QUALITY CHECKS
    # --------------------------------------------------------

    print("\n[8/8] RUNNING BIGQUERY QUALITY CHECKS")

    run_all_quality_checks(
        client=client,
        project_id=PROJECT_ID,
        dataset_name=BIGQUERY_DATASET
    )


if __name__ == "__main__":
    main()