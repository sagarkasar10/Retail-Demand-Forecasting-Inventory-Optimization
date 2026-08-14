from src.extraction.sales_loader import (
    extract_sales_data,
    validate_sales_columns,
    prepare_sales_for_bigquery,
)

from src.extraction.calendar_loader import (
    extract_calendar_data,
    validate_calendar_columns,
    prepare_calendar_for_bigquery,
)

from src.extraction.prices_loader import (
    extract_prices_data,
    validate_prices_columns,
    prepare_prices_for_bigquery,
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

from src.profiling.sales_profile import (
    profile_sales_data,
    print_sales_profile,
    get_sales_by_store,
    get_sales_by_department,
)

from src.profiling.calendar_price_profile import (
    profile_calendar_data,
    print_calendar_profile,
    profile_price_data,
    print_price_profile,
)

from src.warehouse.bigquery_client import (
    get_bigquery_client,
    create_dataset_if_not_exists,
)

from src.warehouse.bigquery_tables import (
    create_all_clean_tables,
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
    print("WEEK 1 - DAY 5 PIPELINE")
    print("=" * 70)

    # --------------------------------------------------------
    # STEP 1 - BIGQUERY
    # --------------------------------------------------------

    print("\n[1/9] INITIALIZING BIGQUERY")

    client = get_bigquery_client(
        project_id=PROJECT_ID
    )

    create_dataset_if_not_exists(
        client=client,
        dataset_name=BIGQUERY_DATASET,
        location="US"
    )

    # --------------------------------------------------------
    # STEP 2 - SALES
    # --------------------------------------------------------

    print("\n[2/9] LOADING SALES DATA")

    sales_df = extract_sales_data(
        SALES_PATH
    )

    validate_sales_columns(
        sales_df
    )

    check_sales_values(
        sales_df
    )

    sales_df = clean_sales_data(
        sales_df
    )

    sales_profile = profile_sales_data(
        sales_df
    )

    print_sales_profile(
        sales_profile
    )

    # --------------------------------------------------------
    # STEP 3 - CALENDAR
    # --------------------------------------------------------

    print("\n[3/9] LOADING CALENDAR DATA")

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

    calendar_profile = profile_calendar_data(
        calendar_df
    )

    print_calendar_profile(
        calendar_profile
    )

    # --------------------------------------------------------
    # STEP 4 - PRICES
    # --------------------------------------------------------

    print("\n[4/9] LOADING PRICING DATA")

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

    price_profile = profile_price_data(
        prices_df
    )

    print_price_profile(
        price_profile
    )

    # --------------------------------------------------------
    # STEP 5 - PREPARE FOR BIGQUERY
    # --------------------------------------------------------

    print("\n[5/9] PREPARING DATA")

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
    # STEP 6 - STORE PROFILING OUTPUT
    # --------------------------------------------------------

    print("\n[6/9] SALES ANALYSIS")

    sales_by_store = get_sales_by_store(
        sales_df
    )

    sales_by_department = (
        get_sales_by_department(
            sales_df
        )
    )

    print("\nTop stores by sales:")

    print(
        sales_by_store.head(10).to_string(
            index=False
        )
    )

    print("\nTop departments by sales:")

    print(
        sales_by_department.head(10).to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # STEP 7 - CREATE CLEAN TABLES
    # --------------------------------------------------------

    print("\n[7/9] CREATING CLEAN BIGQUERY TABLES")

    create_all_clean_tables(
        client=client,
        project_id=PROJECT_ID,
        dataset_name=BIGQUERY_DATASET
    )

    # --------------------------------------------------------
    # STEP 8 - RUN QUALITY CHECKS
    # --------------------------------------------------------

    print("\n[8/9] RUNNING FINAL QUALITY CHECKS")

    run_all_quality_checks(
        client=client,
        project_id=PROJECT_ID,
        dataset_name=BIGQUERY_DATASET
    )

    # --------------------------------------------------------
    # STEP 9 - COMPLETE
    # --------------------------------------------------------

    print("\nCreated BigQuery tables:")

    print(
        f"✓ {PROJECT_ID}."
        f"{BIGQUERY_DATASET}.clean_sales"
    )

    print(
        f"✓ {PROJECT_ID}."
        f"{BIGQUERY_DATASET}.clean_calendar"
    )

    print(
        f"✓ {PROJECT_ID}."
        f"{BIGQUERY_DATASET}.clean_prices"
    )


if __name__ == "__main__":
    main()
