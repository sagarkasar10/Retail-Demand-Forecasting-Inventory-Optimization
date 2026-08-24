SELECT
    id,
    date
FROM {{ ref('int_sales_with_calendar') }}
WHERE wm_yr_wk IS NULL