from src.validation.pipeline_validation import (
    validate_all_data
)

from src.profiling.data_summary import (
    print_pipeline_summary
)

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

from src.warehouse.bigquery_client import (
    get_bigquery_client,
    create_dataset_if_not_exists,
    load_dataframe_to_bigquery,
)

from src.warehouse.bigquery_tables import (
    create_all_clean_tables,
)

from src.warehouse.warehouse_validation import (
    verify_week1_tables
)

from src.validation.quality_report import (
    create_quality_report,
    print_quality_report,
    quality_report_passed,
)

import logging

from src.forecasting.data_loader import (
    load_daily_sales,
    validate_daily_sales,
)
from src.forecasting.train_test_split import (
    chronological_split,
    get_split_summary,
)
from src.forecasting.prophet_features import (
    prepare_prophet_data,
)
from src.forecasting.prophet_model import (
    train_and_forecast_prophet,
    create_prophet_forecast_output,
)
from src.forecasting.lightgbm_features import (
    prepare_lightgbm_features,
)
from src.forecasting.lightgbm_model import (
    train_lightgbm_model,
    predict_lightgbm,
    DEFAULT_FEATURES,
)
from src.forecasting.evaluation import (
    evaluate_forecast,
)
from src.forecasting.model_comparison import (
    evaluate_model_predictions,
    compare_model_metrics,
    select_best_model,
)


# ============================================================
# CONFIGURATION
# ============================================================


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
# MAIN PIPELINE
# ============================================================

def main():

    print("\n")
    print("=" * 70)
    print(
        "RETAIL DEMAND FORECASTING & "
        "INVENTORY OPTIMIZATION"
    )
    print("WEEK 1 - DAY 6 PIPELINE")
    print("=" * 70)

    # --------------------------------------------------------
    # 1. INITIALIZE BIGQUERY
    # --------------------------------------------------------

    print("\n[1/9] INITIALIZING BIGQUERY")

    client = get_bigquery_client()

    PROJECT_ID = client.project

    create_dataset_if_not_exists(
        client=client,
        dataset_name=BIGQUERY_DATASET,
        location="US"
    )

    # --------------------------------------------------------
    # 2. LOAD AND CLEAN SALES
    # --------------------------------------------------------

    print("\n[2/8] PROCESSING SALES DATA")

    raw_sales_df = extract_sales_data(
        SALES_PATH
    )

    validate_sales_columns(
        raw_sales_df
    )

    check_sales_values(
        raw_sales_df
    )

    sales_df = clean_sales_data(
        raw_sales_df
    )

    # --------------------------------------------------------
    # 3. LOAD AND CLEAN CALENDAR
    # --------------------------------------------------------

    print("\n[3/8] PROCESSING CALENDAR DATA")

    raw_calendar_df = extract_calendar_data(
        CALENDAR_PATH
    )

    validate_calendar_columns(
        raw_calendar_df
    )

    validate_calendar_dates(
        raw_calendar_df
    )

    calendar_df = clean_calendar_data(
        raw_calendar_df
    )

    # --------------------------------------------------------
    # 4. LOAD AND CLEAN PRICES
    # --------------------------------------------------------

    print("\n[4/8] PROCESSING PRICING DATA")

    raw_prices_df = extract_prices_data(
        PRICES_PATH
    )

    validate_prices_columns(
        raw_prices_df
    )

    validate_pricing_data(
        raw_prices_df
    )

    prices_df = clean_pricing_data(
        raw_prices_df
    )

    # --------------------------------------------------------
    # 5. DATAFRAME VALIDATION
    # --------------------------------------------------------

    print("\n[5/8] RUNNING DATAFRAME VALIDATION")

    validate_all_data(
        sales_df=sales_df,
        calendar_df=calendar_df,
        prices_df=prices_df
    )

    # --------------------------------------------------------
    # 6. LOAD RAW DATA INTO BIGQUERY
    # --------------------------------------------------------

    print("\n[6/9] LOADING RAW DATA INTO BIGQUERY")

    load_dataframe_to_bigquery(
        client=client,
        dataframe=raw_sales_df,
        dataset_name=BIGQUERY_DATASET,
        table_name="raw_sales",
    )

    load_dataframe_to_bigquery(
        client=client,
        dataframe=raw_calendar_df,
        dataset_name=BIGQUERY_DATASET,
        table_name="raw_calendar",
    )

    load_dataframe_to_bigquery(
        client=client,
        dataframe=raw_prices_df,
        dataset_name=BIGQUERY_DATASET,
        table_name="raw_prices",
    )

    print("✓ Raw BigQuery tables loaded successfully")

    print("\n[7/9] RUNNING BIGQUERY RAW DATA QUALITY CHECKS")

    run_all_quality_checks(
        client=client,
        project_id=PROJECT_ID,
        dataset_name=BIGQUERY_DATASET,
    )

    # --------------------------------------------------------
    # 7. PREPARE DATA FOR BIGQUERY
    # --------------------------------------------------------

    print("\n[7/9] PREPARING DATA FOR BIGQUERY")

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
    # 8. CREATE CLEAN BIGQUERY TABLES
    # --------------------------------------------------------

    print("\n[8/9] CREATING CLEAN BIGQUERY TABLES")

    create_all_clean_tables(
        client=client,
        project_id=PROJECT_ID,
        dataset_name=BIGQUERY_DATASET
    )

    # --------------------------------------------------------
    # 9. FINAL SUMMARY
    # --------------------------------------------------------

    print("\n[9/9] GENERATING FINAL SUMMARY")

    print_pipeline_summary(
        sales_df=sales_df,
        calendar_df=calendar_df,
        prices_df=prices_df
    )

    print("\nClean BigQuery tables:")

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

    # ============================================================
    # FINAL WEEK 1 VERIFICATION
    # ============================================================

    print("\n[FINAL] VERIFYING CLEAN TABLE QUALITY")

    run_all_quality_checks(
        client=client,
        project_id=PROJECT_ID,
        dataset_name=BIGQUERY_DATASET,
        include_clean=True,
    )

    print("\n[FINAL] VERIFYING BIGQUERY TABLES")

    warehouse_status = verify_week1_tables(
        client=client,
        project_id=PROJECT_ID,
        dataset_name=BIGQUERY_DATASET
    )


    # ============================================================
    # FINAL QUALITY REPORT
    # ============================================================

    print("\n[FINAL] GENERATING QUALITY REPORT")

    quality_report = create_quality_report(
        sales_df=sales_df,
        calendar_df=calendar_df,
        prices_df=prices_df
    )

    print_quality_report(
        quality_report
    )


    # ============================================================
    # FINAL STATUS
    # ============================================================

    data_quality_status = quality_report_passed(
        quality_report
    )


    if warehouse_status and data_quality_status:

        print("\n")
        print("=" * 70)
        print("✓ WEEK 1 COMPLETED SUCCESSFULLY")
        print("=" * 70)

        print("\nStatus:")
        print("✓ BigQuery tables verified")
        print("✓ Sales data validated")
        print("✓ Calendar data validated")
        print("✓ Pricing data validated")
        print("✓ Clean tables verified")
        print("✓ Data quality checks passed")
        print("✓ ETL pipeline ready for Week 2")

    else:

        print("\n")
        print("=" * 70)
        print("✗ WEEK 1 VALIDATION FAILED")
        print("=" * 70)

        print(
            "\nPlease review the validation errors "
            "before starting Week 2."
        )

        raise RuntimeError(
            "Week 1 validation failed."
        )

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def run_forecasting_pipeline():
    """Run the Week 3 Day 3 forecasting pipeline."""

    logger.info(
        "Starting Week 3 Day 3 forecasting pipeline."
    )

    daily_sales = load_daily_sales()

    validate_daily_sales(
        daily_sales
    )

    train_df, validation_df, test_df = chronological_split(
        daily_sales,
        validation_days=30,
        test_days=30,
    )

    logger.info(
        "Split summary: %s",
        get_split_summary(
            train_df,
            validation_df,
            test_df,
        ),
    )

    logger.info(
        "Training Prophet."
    )

    prophet_train = prepare_prophet_data(
        train_df
    )

    prophet_forecast = train_and_forecast_prophet(
        prophet_train,
        periods=30,
    )

    prophet_output = create_prophet_forecast_output(
        prophet_forecast
    )

    logger.info(
        "Prophet generated %s forecast rows.",
        len(prophet_output),
    )

    logger.info(
        "Preparing LightGBM training features."
    )

    lightgbm_train = prepare_lightgbm_features(
        train_df
    )

    lightgbm_train = lightgbm_train.dropna(
        subset=DEFAULT_FEATURES + ["sales"]
    )

    lightgbm_model = train_lightgbm_model(
        lightgbm_train
    )

    logger.info(
        "LightGBM model trained."
    )

    logger.info(
        "Preparing LightGBM validation features."
    )

    combined_history = daily_sales[
        daily_sales["date"] <= validation_df["date"].max()
    ].copy()

    validation_features = prepare_lightgbm_features(
        combined_history
    )

    validation_features = validation_features[
        validation_features["date"].isin(
            validation_df["date"]
        )
    ].copy()

    validation_features = validation_features.dropna(
        subset=DEFAULT_FEATURES + ["sales"]
    )

    model_metrics = []

    if not validation_features.empty:
        lightgbm_predictions = predict_lightgbm(
            lightgbm_model,
            validation_features,
            DEFAULT_FEATURES,
        )

        lightgbm_metrics = evaluate_model_predictions(
            validation_features["sales"],
            lightgbm_predictions,
            "LightGBM",
        )

        model_metrics.append(
            lightgbm_metrics
        )

        logger.info(
            "LightGBM metrics: %s",
            lightgbm_metrics,
        )

    logger.info(
        "Evaluating Prophet on the validation period."
    )

    prophet_validation_train = prepare_prophet_data(
        train_df
    )

    prophet_validation_model_forecast = train_and_forecast_prophet(
        prophet_validation_train,
        periods=30,
    )

    prophet_actual = validation_df[
        ["date", "sales"]
    ].copy()

    prophet_actual["date"] = pd.to_datetime(
        prophet_actual["date"]
    )

    prophet_predictions = (
        prophet_validation_model_forecast
        .rename(
            columns={
                "ds": "date",
                "yhat": "predicted_demand",
            }
        )
        [["date", "predicted_demand"]]
    )

    prophet_validation = prophet_actual.merge(
        prophet_predictions,
        on="date",
        how="inner",
    )

    if not prophet_validation.empty:
        prophet_metrics = evaluate_model_predictions(
            prophet_validation["sales"],
            prophet_validation["predicted_demand"],
            "Prophet",
        )

        model_metrics.append(
            prophet_metrics
        )

        logger.info(
            "Prophet metrics: %s",
            prophet_metrics,
        )

    if model_metrics:
        comparison = compare_model_metrics(
            model_metrics
        )

        best_model = select_best_model(
            comparison,
            metric="wape",
        )

        logger.info(
            "Model comparison:\n%s",
            comparison.to_string(index=False),
        )

        logger.info(
            "Best model based on WAPE: %s",
            best_model,
        )
    else:
        comparison = None
        best_model = None

        logger.warning(
            "No model metrics were generated."
        )

    logger.info(
        "Week 3 Day 3 forecasting pipeline completed."
    )

    return {
        "prophet_forecast": prophet_output,
        "lightgbm_model": lightgbm_model,
        "comparison": comparison,
        "best_model": best_model,
        "train": train_df,
        "validation": validation_df,
        "test": test_df,
    }

if __name__ == "__main__":
    main()
    run_forecasting_pipeline()
    
    
    