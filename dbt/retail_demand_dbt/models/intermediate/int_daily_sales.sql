WITH sales_source AS (

    SELECT *
    FROM {{ ref('stg_sales') }}

),

calendar_days AS (

    SELECT
        day_number,
        date
    FROM {{ ref('int_sales_calendar_mapping') }}
    
)

sales_json AS (

    SELECT
        s.*,
        TO_JSON_STRING(s) AS sales_json
    FROM sales_source AS s

),

daily_sales AS (

    SELECT
        s.id,
        s.item_id,
        s.dept_id,
        s.cat_id,
        s.store_id,
        s.state_id,
        CAST(REPLACE(day_column, 'd_', '') AS INT64) AS day_number,
        SAFE_CAST(
            JSON_VALUE(
                s.sales_json,
                CONCAT('$.', day_column)
            ) AS INT64
        ) AS sales

    FROM sales_json AS s

    CROSS JOIN UNNEST(
        JSON_KEYS(
            JSON_QUERY(s.sales_json, '$')
        )
    ) AS day_column

    WHERE STARTS_WITH(day_column, 'd_')

)

SELECT
    d.id,
    d.item_id,
    d.dept_id,
    d.cat_id,
    d.store_id,
    d.state_id,
    c.date,
    d.sales

FROM daily_sales AS d

INNER JOIN calendar_days AS c
    ON d.day_number = c.day_number