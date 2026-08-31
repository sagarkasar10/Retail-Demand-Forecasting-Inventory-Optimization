# Retail Demand Forecasting dbt Layer

## Data Lineage

BigQuery Raw Tables
        |
        +-- raw_sales
        |
        +-- raw_calendar
        |
        +-- raw_prices
        |
        v
      Sources
        |
        v
     Staging
        |
        +-- stg_sales
        +-- stg_calendar
        +-- stg_prices
        |
        v
   Intermediate
        |
        +-- int_sales_calender_mapping
        +-- int_daily_sales
        +-- int_sales_with_calendar
        +-- int_sales_with_prices
        +-- int_sales_events
        |
        v
      Marts
        |
        +-- fct_daily_sales
        +-- fct_weekly_sales
        +-- fct_monthly_sales
        +-- fct_item_store_sales
        +-- dim_product
        +-- dim_store
        |
        v
Week 3 Forecasting
        |
        +-- Prophet
        +-- LightGBM
        +-- Forecast Outputs

Model Layers

Staging

The staging layer standardizes the Week 1 raw BigQuery tables without performing business-level aggregation.

Intermediate

The intermediate layer converts M5 sales into daily format and enriches sales with calendar, event and pricing data.

Marts

The mart layer provides daily, weekly and monthly analytical datasets for demand forecasting and inventory optimization.

Forecasting Input

The primary Week 3 forecasting dataset is:

fct_daily_sales

Its grain is:

item + store + date

Weekly and monthly aggregations are available through:

fct_weekly_sales

fct_monthly_sales
