
-- ============================================================
-- 1. VERIFY CLEAN TABLES EXIST
-- ============================================================

SELECT
    table_name
FROM `GCP_PROJECT_ID.retail_demand.INFORMATION_SCHEMA.TABLES`
WHERE table_name IN (
    'clean_sales',
    'clean_calendar',
    'clean_prices'
)
ORDER BY table_name;


-- ============================================================
-- 2. CLEAN SALES - ROW COUNT
-- ============================================================

SELECT
    COUNT(*) AS total_rows
FROM `GCP_PROJECT_ID.retail_demand.clean_sales`;


-- ============================================================
-- 3. CLEAN SALES - REQUIRED FIELD CHECK
-- ============================================================

SELECT
    COUNT(*) AS total_rows,

    COUNTIF(id IS NULL) AS null_id_count,

    COUNTIF(item_id IS NULL) AS null_item_id_count,

    COUNTIF(dept_id IS NULL) AS null_dept_id_count,

    COUNTIF(cat_id IS NULL) AS null_cat_id_count,

    COUNTIF(store_id IS NULL) AS null_store_id_count,

    COUNTIF(state_id IS NULL) AS null_state_id_count

FROM `GCP_PROJECT_ID.retail_demand.clean_sales`;


-- ============================================================
-- 4. CLEAN SALES - DUPLICATE ID CHECK
-- ============================================================

SELECT
    id,
    COUNT(*) AS duplicate_count
FROM `GCP_PROJECT_ID.retail_demand.clean_sales`
GROUP BY id
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;


-- ============================================================
-- 5. CLEAN SALES - UNIQUE DIMENSIONS
-- ============================================================

SELECT
    COUNT(DISTINCT id) AS unique_ids,
    COUNT(DISTINCT item_id) AS unique_items,
    COUNT(DISTINCT store_id) AS unique_stores,
    COUNT(DISTINCT dept_id) AS unique_departments,
    COUNT(DISTINCT cat_id) AS unique_categories,
    COUNT(DISTINCT state_id) AS unique_states
FROM `GCP_PROJECT_ID.retail_demand.clean_sales`;


-- ============================================================
-- 6. CLEAN CALENDAR - BASIC VALIDATION
-- ============================================================

SELECT
    COUNT(*) AS total_rows,

    COUNTIF(date IS NULL) AS null_date_count,

    COUNTIF(wm_yr_wk IS NULL) AS null_week_count,

    COUNTIF(month IS NULL) AS null_month_count,

    COUNTIF(year IS NULL) AS null_year_count,

    COUNT(DISTINCT date) AS unique_dates,

    MIN(date) AS minimum_date,

    MAX(date) AS maximum_date

FROM `GCP_PROJECT_ID.retail_demand.clean_calendar`;


-- ============================================================
-- 7. CLEAN CALENDAR - DUPLICATE DATE CHECK
-- ============================================================

SELECT
    date,
    COUNT(*) AS duplicate_count
FROM `GCP_PROJECT_ID.retail_demand.clean_calendar`
GROUP BY date
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;


-- ============================================================
-- 8. CLEAN CALENDAR - INVALID MONTH
-- ============================================================

SELECT
    COUNT(*) AS invalid_month_count
FROM `GCP_PROJECT_ID.retail_demand.clean_calendar`
WHERE month IS NOT NULL
  AND (
      month < 1
      OR month > 12
  );


-- ============================================================
-- 9. CLEAN CALENDAR - INVALID WEEKDAY
-- ============================================================

SELECT
    COUNT(*) AS invalid_wday_count
FROM `GCP_PROJECT_ID.retail_demand.clean_calendar`
WHERE wday IS NOT NULL
  AND (
      wday < 1
      OR wday > 7
  );


-- ============================================================
-- 10. CLEAN PRICES - BASIC VALIDATION
-- ============================================================

SELECT
    COUNT(*) AS total_rows,

    COUNTIF(store_id IS NULL) AS null_store_id_count,

    COUNTIF(item_id IS NULL) AS null_item_id_count,

    COUNTIF(wm_yr_wk IS NULL) AS null_week_count,

    COUNTIF(sell_price IS NULL) AS null_price_count,

    COUNTIF(sell_price < 0) AS negative_price_count

FROM `GCP_PROJECT_ID.retail_demand.clean_prices`;


-- ============================================================
-- 11. CLEAN PRICES - DUPLICATE BUSINESS KEY
-- ============================================================

SELECT
    store_id,
    item_id,
    wm_yr_wk,
    COUNT(*) AS duplicate_count
FROM `GCP_PROJECT_ID.retail_demand.clean_prices`
GROUP BY
    store_id,
    item_id,
    wm_yr_wk
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;


-- ============================================================
-- 12. CLEAN PRICES - PRICE STATISTICS
-- ============================================================

SELECT
    MIN(sell_price) AS minimum_price,
    MAX(sell_price) AS maximum_price,
    AVG(sell_price) AS average_price
FROM `GCP_PROJECT_ID.retail_demand.clean_prices`;


-- ============================================================
-- 13. RAW VS CLEAN ROW COUNTS
-- ============================================================

SELECT
    'raw_sales' AS table_name,
    COUNT(*) AS row_count
FROM `GCP_PROJECT_ID.retail_demand.raw_sales`

UNION ALL

SELECT
    'clean_sales' AS table_name,
    COUNT(*) AS row_count
FROM `GCP_PROJECT_ID.retail_demand.clean_sales`

UNION ALL

SELECT
    'raw_calendar' AS table_name,
    COUNT(*) AS row_count
FROM `GCP_PROJECT_ID.retail_demand.raw_calendar`

UNION ALL

SELECT
    'clean_calendar' AS table_name,
    COUNT(*) AS row_count
FROM `GCP_PROJECT_ID.retail_demand.clean_calendar`

UNION ALL

SELECT
    'raw_prices' AS table_name,
    COUNT(*) AS row_count
FROM `GCP_PROJECT_ID.retail_demand.raw_prices`

UNION ALL

SELECT
    'clean_prices' AS table_name,
    COUNT(*) AS row_count
FROM `GCP_PROJECT_ID.retail_demand.clean_prices`

ORDER BY table_name;


-- ============================================================
-- 14. SALES DIMENSION CONSISTENCY
-- ============================================================

SELECT
    COUNT(*) AS orphan_item_records
FROM `GCP_PROJECT_ID.retail_demand.clean_sales` s
WHERE s.item_id IS NULL
   OR s.store_id IS NULL;


-- ============================================================
-- 15. FINAL CLEAN TABLE SUMMARY
-- ============================================================

SELECT
    'clean_sales' AS table_name,
    COUNT(*) AS total_rows
FROM `GCP_PROJECT_ID.retail_demand.clean_sales`

UNION ALL

SELECT
    'clean_calendar' AS table_name,
    COUNT(*) AS total_rows
FROM `GCP_PROJECT_ID.retail_demand.clean_calendar`

UNION ALL

SELECT
    'clean_prices' AS table_name,
    COUNT(*) AS total_rows
FROM `GCP_PROJECT_ID.retail_demand.clean_prices`;