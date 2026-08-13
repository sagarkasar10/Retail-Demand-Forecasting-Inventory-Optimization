-- ============================================================
-- 1. ROW COUNT CHECKS
-- ============================================================

SELECT
    'raw_sales' AS table_name,
    COUNT(*) AS row_count
FROM `GCP_PROJECT_ID.retail_demand.raw_sales`;


SELECT
    'raw_calendar' AS table_name,
    COUNT(*) AS row_count
FROM `GCP_PROJECT_ID.retail_demand.raw_calendar`;


SELECT
    'raw_prices' AS table_name,
    COUNT(*) AS row_count
FROM `GCP_PROJECT_ID.retail_demand.raw_prices`;


-- ============================================================
-- 2. SALES TABLE BASIC CHECK
-- ============================================================

SELECT
    COUNT(*) AS total_rows,
    COUNTIF(id IS NULL) AS null_id_count,
    COUNTIF(item_id IS NULL) AS null_item_id_count,
    COUNTIF(store_id IS NULL) AS null_store_id_count,
    COUNTIF(dept_id IS NULL) AS null_dept_id_count,
    COUNTIF(cat_id IS NULL) AS null_cat_id_count,
    COUNTIF(state_id IS NULL) AS null_state_id_count
FROM `GCP_PROJECT_ID.retail_demand.raw_sales`;


-- ============================================================
-- 3. CALENDAR TABLE BASIC CHECK
-- ============================================================

SELECT
    COUNT(*) AS total_rows,
    COUNTIF(date IS NULL) AS null_date_count,
    COUNTIF(wm_yr_wk IS NULL) AS null_week_count
FROM `GCP_PROJECT_ID.retail_demand.raw_calendar`;


-- ============================================================
-- 4. PRICES TABLE BASIC CHECK
-- ============================================================

SELECT
    COUNT(*) AS total_rows,
    COUNTIF(store_id IS NULL) AS null_store_count,
    COUNTIF(item_id IS NULL) AS null_item_count,
    COUNTIF(wm_yr_wk IS NULL) AS null_week_count,
    COUNTIF(sell_price IS NULL) AS null_price_count
FROM `GCP_PROJECT_ID.retail_demand.raw_prices`;


-- ============================================================
-- 5. NEGATIVE PRICE CHECK
-- ============================================================

SELECT
    COUNT(*) AS negative_price_count
FROM `GCP_PROJECT_ID.retail_demand.raw_prices`
WHERE sell_price < 0;


-- ============================================================
-- 6. CALENDAR DATE RANGE
-- ============================================================

SELECT
    MIN(date) AS minimum_date,
    MAX(date) AS maximum_date,
    COUNT(DISTINCT date) AS unique_dates
FROM `GCP_PROJECT_ID.retail_demand.raw_calendar`;


-- ============================================================
-- 7. DUPLICATE PRICE KEY CHECK
-- ============================================================

SELECT
    store_id,
    item_id,
    wm_yr_wk,
    COUNT(*) AS duplicate_count
FROM `GCP_PROJECT_ID.retail_demand.raw_prices`
GROUP BY
    store_id,
    item_id,
    wm_yr_wk
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;


-- ============================================================
-- 8. DUPLICATE CALENDAR DATE CHECK
-- ============================================================

SELECT
    date,
    COUNT(*) AS duplicate_count
FROM `GCP_PROJECT_ID.retail_demand.raw_calendar`
GROUP BY date
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;