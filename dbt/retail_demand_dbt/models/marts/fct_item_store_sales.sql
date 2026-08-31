WITH daily_sales AS (

    SELECT *
    FROM {{ ref('fct_daily_sales') }}

)

SELECT
    item_id,
    store_id,
    dept_id,
    cat_id,
    state_id,

    MIN(date) AS first_sales_date,
    MAX(date) AS last_sales_date,

    SUM(sales) AS total_sales,
    AVG(sales) AS avg_daily_sales,
    MAX(sales) AS max_daily_sales,

    AVG(sell_price) AS avg_sell_price,

    COUNT(DISTINCT date) AS sales_days,
    COUNTIF(is_event_day) AS event_days

FROM daily_sales

GROUP BY
    item_id,
    store_id,
    dept_id,
    cat_id,
    state_id
