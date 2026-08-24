# Retail Demand Forecasting & Inventory Optimization

## Week 1

Week 1 implements the M5 data ingestion, validation, cleaning,
profiling and BigQuery warehouse pipeline.

## Architecture

CSV
→ Raw DataFrames
→ Raw BigQuery Tables
→ Data Quality Checks
→ Clean DataFrames
→ Clean BigQuery Tables
→ Warehouse Validation
→ Final Quality Report

## Required datasets

Place the M5 files in:

data/raw/

Required files:

- sales_train_validation.csv
- calendar.csv
- sell_prices.csv

## Environment

Create `.env`:

GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

## Installation

pip install -r requirements.txt

## Tests

pytest -v

## Run pipeline

python main.py

## BigQuery dataset

retail_demand

Tables:

- raw_sales
- raw_calendar
- raw_prices
- clean_sales
- clean_calendar
- clean_prices

## Week 2 readiness

The clean BigQuery tables produced by Week 1 are the input
for Week 2 transformations and feature engineering.