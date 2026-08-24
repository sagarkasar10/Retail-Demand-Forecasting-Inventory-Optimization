-- ============================================================
-- WEEK 1 BIGQUERY TABLE DEFINITIONS
-- Dataset: retail_demand
-- ============================================================

-- RAW TABLES
-- Raw tables are loaded directly from the M5 source datasets.
--
-- raw_sales
--   id STRING
--   item_id STRING
--   dept_id STRING
--   cat_id STRING
--   store_id STRING
--   state_id STRING
--   d_1 ... d_n INTEGER
--
-- raw_calendar
--   date DATE
--   wm_yr_wk INTEGER
--   weekday STRING
--   wday INTEGER
--   month INTEGER
--   year INTEGER
--   event_name_1 STRING
--   event_type_1 STRING
--   event_name_2 STRING
--   event_type_2 STRING
--   snap_CA INTEGER
--   snap_TX INTEGER
--   snap_WI INTEGER
--
-- raw_prices
--   store_id STRING
--   item_id STRING
--   wm_yr_wk INTEGER
--   sell_price FLOAT64


-- ============================================================
-- CLEAN TABLES
-- ============================================================

-- clean_sales
-- Standardized sales table.
-- M5 daily sales remain in wide format during Week 1.

-- clean_calendar
-- Standardized calendar data.

-- clean_prices
-- Standardized pricing data.