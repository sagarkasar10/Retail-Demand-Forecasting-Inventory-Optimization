WITH sales_data AS (

    SELECT *
    FROM {{ ref('int_sales_events') }}

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
    event_name,
    event_type,
    is_event_day,
    snap_CA,
    snap_TX,
    snap_WI

FROM sales_data