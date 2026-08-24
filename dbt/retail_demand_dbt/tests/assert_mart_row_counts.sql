WITH row_counts AS (

    SELECT
        (SELECT COUNT(*) FROM {{ ref('fct_daily_sales') }}) AS daily_count,
        (SELECT COUNT(*) FROM {{ ref('fct_weekly_sales') }}) AS weekly_count,
        (SELECT COUNT(*) FROM {{ ref('fct_monthly_sales') }}) AS monthly_count

)

SELECT *
FROM row_counts
WHERE daily_count = 0
   OR weekly_count = 0
   OR monthly_count = 0