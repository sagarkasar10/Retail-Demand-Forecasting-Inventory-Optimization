
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


-- ============================================================
-- 16. CLEAN TABLE ROW COUNT STATUS
-- ============================================================

WITH table_counts AS (

    SELECT
        'clean_sales' AS table_name,
        COUNT(*) AS row_count
    FROM `GCP_PROJECT_ID.retail_demand.clean_sales`

    UNION ALL

    SELECT
        'clean_calendar' AS table_name,
        COUNT(*) AS row_count
    FROM `GCP_PROJECT_ID.retail_demand.clean_calendar`

    UNION ALL

    SELECT
        'clean_prices' AS table_name,
        COUNT(*) AS row_count
    FROM `GCP_PROJECT_ID.retail_demand.clean_prices`
)

SELECT
    table_name,
    row_count,
    CASE
        WHEN row_count > 0 THEN 'PASS'
        ELSE 'FAIL'
    END AS validation_status
FROM table_counts
ORDER BY table_name;


-- ============================================================
-- 17. CLEAN SALES KEY VALIDATION
-- ============================================================

SELECT
    COUNT(*) AS total_rows,

    COUNTIF(id IS NULL) AS null_ids,

    COUNTIF(item_id IS NULL) AS null_items,

    COUNTIF(store_id IS NULL) AS null_stores,

    COUNTIF(dept_id IS NULL) AS null_departments,

    COUNTIF(cat_id IS NULL) AS null_categories

FROM `GCP_PROJECT_ID.retail_demand.clean_sales`;


-- ============================================================
-- 18. CLEAN CALENDAR DATE CONTINUITY
-- ============================================================

WITH ordered_dates AS (

    SELECT
        date,
        LAG(date) OVER (
            ORDER BY date
        ) AS previous_date
    FROM `GCP_PROJECT_ID.retail_demand.clean_calendar`
)

SELECT
    COUNT(*) AS missing_date_gap_count
FROM ordered_dates
WHERE previous_date IS NOT NULL
  AND DATE_DIFF(
      date,
      previous_date,
      DAY
  ) > 1;


-- ============================================================
-- 19. CLEAN PRICES - INVALID PRICES
-- ============================================================

SELECT
    COUNT(*) AS invalid_price_count
FROM `GCP_PROJECT_ID.retail_demand.clean_prices`
WHERE sell_price IS NULL
   OR sell_price < 0;


-- ============================================================
-- 20. FINAL VALIDATION STATUS
-- ============================================================

WITH validation AS (

    SELECT
        (
            SELECT COUNT(*)
            FROM `GCP_PROJECT_ID.retail_demand.clean_sales`
        ) AS sales_rows,

        (
            SELECT COUNT(*)
            FROM `GCP_PROJECT_ID.retail_demand.clean_calendar`
        ) AS calendar_rows,

        (
            SELECT COUNT(*)
            FROM `GCP_PROJECT_ID.retail_demand.clean_prices`
        ) AS price_rows

)

SELECT
    sales_rows,
    calendar_rows,
    price_rows,

    CASE
        WHEN sales_rows > 0
         AND calendar_rows > 0
         AND price_rows > 0
        THEN 'PASS'
        ELSE 'FAIL'
    END AS overall_status

FROM validation;

-- ============================================================
-- 21. VERIFY ALL WEEK 1 TABLES
-- ============================================================

SELECT
    table_name
FROM `GCP_PROJECT_ID.retail_demand.INFORMATION_SCHEMA.TABLES`
WHERE table_name IN (
    'raw_sales',
    'raw_calendar',
    'raw_prices',
    'clean_sales',
    'clean_calendar',
    'clean_prices'
)
ORDER BY table_name;


-- ============================================================
-- 22. FINAL CALENDAR DATE RANGE CHECK
-- ============================================================

SELECT
    MIN(date) AS minimum_date,
    MAX(date) AS maximum_date,
    COUNT(DISTINCT date) AS unique_dates,
    COUNT(*) AS total_rows
FROM `GCP_PROJECT_ID.retail_demand.clean_calendar`;

-- ============================================================
-- 23. FINAL PRICE SUMMARY
-- ============================================================

SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT store_id) AS unique_stores,
    COUNT(DISTINCT item_id) AS unique_items,
    COUNT(DISTINCT wm_yr_wk) AS unique_weeks,
    MIN(sell_price) AS minimum_price,
    MAX(sell_price) AS maximum_price,
    AVG(sell_price) AS average_price
FROM `GCP_PROJECT_ID.retail_demand.clean_prices`;


-- ============================================================
-- 24. FINAL WEEK 1 PASS / FAIL STATUS
-- ============================================================

WITH validation AS (

    SELECT

        -- ----------------------------------------------------
        -- SALES
        -- ----------------------------------------------------

        (
            SELECT COUNT(*)
            FROM `GCP_PROJECT_ID.retail_demand.clean_sales`
        ) AS sales_rows,

        (
            SELECT COUNT(*)
            FROM `GCP_PROJECT_ID.retail_demand.clean_sales`
            WHERE id IS NULL
               OR item_id IS NULL
               OR store_id IS NULL
               OR dept_id IS NULL
               OR cat_id IS NULL
               OR state_id IS NULL
        ) AS invalid_sales_rows,


        -- ----------------------------------------------------
        -- CALENDAR
        -- ----------------------------------------------------

        (
            SELECT COUNT(*)
            FROM `GCP_PROJECT_ID.retail_demand.clean_calendar`
        ) AS calendar_rows,

        (
            SELECT COUNT(*)
            FROM `GCP_PROJECT_ID.retail_demand.clean_calendar`
            WHERE date IS NULL
               OR month IS NULL
               OR year IS NULL
               OR month < 1
               OR month > 12
               OR wday < 1
               OR wday > 7
        ) AS invalid_calendar_rows,


        -- ----------------------------------------------------
        -- PRICES
        -- ----------------------------------------------------

        (
            SELECT COUNT(*)
            FROM `GCP_PROJECT_ID.retail_demand.clean_prices`
        ) AS price_rows,

        (
            SELECT COUNT(*)
            FROM `GCP_PROJECT_ID.retail_demand.clean_prices`
            WHERE store_id IS NULL
               OR item_id IS NULL
               OR wm_yr_wk IS NULL
               OR sell_price IS NULL
               OR sell_price < 0
        ) AS invalid_price_rows

)

SELECT

    sales_rows,

    calendar_rows,

    price_rows,

    invalid_sales_rows,

    invalid_calendar_rows,

    invalid_price_rows,

    CASE

        WHEN sales_rows > 0
         AND calendar_rows > 0
         AND price_rows > 0
         AND invalid_sales_rows = 0
         AND invalid_calendar_rows = 0
         AND invalid_price_rows = 0

        THEN 'WEEK 1 PASS'

        ELSE 'WEEK 1 REVIEW REQUIRED'

    END AS final_status

FROM validation;

