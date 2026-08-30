WITH sales_calendar AS (

    SELECT *
    FROM {{ ref('int_sales_with_calendar') }}

),

prices AS (

    SELECT
        store_id,
        item_id,
        wm_yr_wk,
        sell_price
    FROM {{ ref('stg_prices') }}

)

SELECT
    s.id,
    s.item_id,
    s.dept_id,
    s.cat_id,
    s.store_id,
    s.state_id,
    s.date,
    s.wm_yr_wk,
    s.sales,
    p.sell_price,
    s.weekday,
    s.wday,
    s.month,
    s.year,
    s.event_name_1,
    s.event_type_1,
    s.event_name_2,
    s.event_type_2,
    s.snap_CA,
    s.snap_TX,
    s.snap_WI

FROM sales_calendar AS s

LEFT JOIN prices AS p
    ON s.store_id = p.store_id
    AND s.item_id = p.item_id
    AND s.wm_yr_wk = p.wm_yr_wk