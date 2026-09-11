import pandas as pd

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
from src.forecasting.week3_pipeline import (
    run_week3_pipeline,
)

from src.forecasting.model_comparison import (
    evaluate_model_predictions,
    compare_prophet_and_lightgbm,
    get_best_forecasting_model,
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
    """Run the Week 3 Day 5 LightGBM pipeline."""

    logger.info(
        "Starting Week 3 Day 5 LightGBM pipeline."
    )

    daily_sales = load_daily_sales()

    validate_daily_sales(
        daily_sales
    )

    logger.info(
        "Loaded %s sales rows.",
        len(daily_sales),
    )

    train_df, validation_df, test_df = chronological_split(
        daily_sales,
        validation_days=30,
        test_days=30,
    )

    logger.info(
        "Data split: %s",
        get_split_summary(
            train_df,
            validation_df,
            test_df,
        ),
    )

    logger.info(
        "Creating LightGBM training features."
    )

    train_features = prepare_lightgbm_features(
        train_df
    )

    train_features = train_features.dropna(
        subset=["sales"]
    )

    feature_columns = get_feature_columns(
        train_features
    )

    train_features = train_features.dropna(
        subset=feature_columns + ["sales"]
    )

    if train_features.empty:
        raise ValueError(
            "No valid LightGBM training rows available."
        )

    logger.info(
        "LightGBM feature count: %s",
        len(feature_columns),
    )

    logger.info(
        "Creating validation features."
    )

    history_until_validation = daily_sales[
        daily_sales["date"]
        <= validation_df["date"].max()
    ].copy()

    validation_features = prepare_lightgbm_features(
        history_until_validation
    )

    validation_dates = set(
        validation_df["date"].dt.normalize()
    )

    validation_features = validation_features[
        validation_features["date"]
        .dt.normalize()
        .isin(validation_dates)
    ].copy()

    validation_features = validation_features.dropna(
        subset=feature_columns + ["sales"]
    )

    if validation_features.empty:
        raise ValueError(
            "No valid LightGBM validation rows available."
        )

    logger.info(
        "Tuning LightGBM parameters."
    )

    best_model, tuning_results = tune_lightgbm(
        train_df=train_features,
        validation_df=validation_features,
        feature_columns=feature_columns,
    )

    best_parameters = get_best_parameters(
        tuning_results
    )

    logger.info(
        "Best LightGBM parameters: %s",
        best_parameters,
    )

    logger.info(
        "LightGBM tuning results:\n%s",
        tuning_results.to_string(index=False),
    )

    validation_predictions = predict_lightgbm(
        best_model,
        validation_features,
        feature_columns,
    )

    validation_metrics = evaluate_model_predictions(
        validation_features["sales"],
        validation_predictions,
        "LightGBM",
    )

    logger.info(
        "LightGBM validation metrics: %s",
        validation_metrics,
    )

    validation_output = create_lightgbm_forecast_output(
        validation_features,
        validation_predictions,
        model_name="LightGBM",
    )

    validate_forecast_output(
        validation_output
    )

    logger.info(
        "Validation forecast summary: %s",
        calculate_forecast_summary(
            validation_output
        ),
    )

    logger.info(
        "Preparing test forecast features."
    )

    history_until_test = daily_sales[
        daily_sales["date"]
        <= test_df["date"].max()
    ].copy()

    test_features = prepare_lightgbm_features(
        history_until_test
    )

    test_dates = set(
        test_df["date"].dt.normalize()
    )

    test_features = test_features[
        test_features["date"]
        .dt.normalize()
        .isin(test_dates)
    ].copy()

    test_features = test_features.dropna(
        subset=feature_columns + ["sales"]
    )

    if test_features.empty:
        raise ValueError(
            "No valid LightGBM test rows available."
        )

    test_predictions = predict_lightgbm(
        best_model,
        test_features,
        feature_columns,
    )

    test_metrics = evaluate_model_predictions(
        test_features["sales"],
        test_predictions,
        "LightGBM",
    )

    logger.info(
        "LightGBM test metrics: %s",
        test_metrics,
    )

    test_output = create_lightgbm_forecast_output(
        test_features,
        test_predictions,
        model_name="LightGBM",
    )

    validate_forecast_output(
        test_output
    )

    logger.info(
        "Test forecast summary: %s",
        calculate_forecast_summary(
            test_output
        ),
    )

    logger.info(
        "Week 3 Day 5 LightGBM pipeline completed."
    )

    return {
        "model": best_model,
        "best_parameters": best_parameters,
        "tuning_results": tuning_results,
        "validation_metrics": validation_metrics,
        "test_metrics": test_metrics,
        "validation_forecast": validation_output,
        "test_forecast": test_output,
        "feature_columns": feature_columns,
        "train": train_features,
        "validation": validation_features,
        "test": test_features,
    }


if __name__ == "__main__":
    main()
    run_forecasting_pipeline()
    
    
    