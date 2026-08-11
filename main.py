from src.extraction.sales_loader import (
    extract_sales_data,
    validate_sales_columns,
    print_sales_summary,
)

from src.extraction.calendar_loader import (
    extract_calendar_data,
    validate_calendar_columns,
    print_calendar_summary,
)

from src.extraction.prices_loader import (
    extract_prices_data,
    validate_prices_columns,
    print_prices_summary,
)

from src.validation.schema_checks import (
    validate_dataset_schema,
)

from src.warehouse.bigquery_client import (
    get_bigquery_client,
    create_dataset_if_not_exists,
)


SALES_PATH = "data/raw/sales_train_validation.csv"
CALENDAR_PATH = "data/raw/calendar.csv"
PRICES_PATH = "data/raw/sell_prices.csv"

BIGQUERY_DATASET = "retail_demand"


def main():
    """
    Main entry point for the Week 1 ETL pipeline.
    """

    print("\n")
    print("=" * 60)
    print("RETAIL DEMAND FORECASTING PIPELINE")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. Create BigQuery client
    # ---------------------------------------------------------

    print("\n[1/4] Initializing BigQuery...")

    client = get_bigquery_client()

    create_dataset_if_not_exists(
        client,
        BIGQUERY_DATASET
    )

    # ---------------------------------------------------------
    # 2. Extract Sales
    # ---------------------------------------------------------

    print("\n[2/4] Extracting sales dataset...")

    sales_df = extract_sales_data(
        SALES_PATH
    )

    validate_sales_columns(
        sales_df
    )

    print_sales_summary(
        sales_df
    )

    # ---------------------------------------------------------
    # 3. Extract Calendar
    # ---------------------------------------------------------

    print("\n[3/4] Extracting calendar dataset...")

    calendar_df = extract_calendar_data(
        CALENDAR_PATH
    )

    validate_calendar_columns(
        calendar_df
    )

    print_calendar_summary(
        calendar_df
    )

    # ---------------------------------------------------------
    # 4. Extract Pricing
    # ---------------------------------------------------------

    print("\n[4/4] Extracting pricing dataset...")

    prices_df = extract_prices_data(
        PRICES_PATH
    )

    validate_prices_columns(
        prices_df
    )

    print_prices_summary(
        prices_df
    )

    # ---------------------------------------------------------
    # Schema validation
    # ---------------------------------------------------------

    print("\nRunning common schema validation...")

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

    print("\n" + "=" * 60)
    print("DAY 2 EXTRACTION PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print("\nBigQuery client:", client.project)
    print("Sales rows:", f"{len(sales_df):,}")
    print("Calendar rows:", f"{len(calendar_df):,}")
    print("Pricing rows:", f"{len(prices_df):,}")
    print()


if __name__ == "__main__":
    main()