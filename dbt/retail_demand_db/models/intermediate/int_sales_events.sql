WITH sales_data AS (

    SELECT *
    FROM {{ ref('int_sales_with_prices') }}

)

SELECT
    id,
    item_id,
    dept_id,
    cat_id,
    store_id,
    state_id,
    date,
    wm_yr_wk,
    sales,
    sell_price,
    weekday,
    wday,
    month,
    year,

    COALESCE(event_name_1, event_name_2) AS event_name,

    COALESCE(event_type_1, event_type_2) AS event_type,

    CASE
        WHEN event_name_1 IS NOT NULL
          OR event_name_2 IS NOT NULL
        THEN TRUE
        ELSE FALSE
    END AS is_event_day,

    snap_CA,
    snap_TX,
    snap_WI

FROM sales_data
