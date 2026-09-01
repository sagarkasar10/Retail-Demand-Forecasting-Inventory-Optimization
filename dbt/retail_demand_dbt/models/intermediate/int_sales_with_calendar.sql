WITH daily_sales AS (

    SELECT *
    FROM {{ ref('int_daily_sales') }}

),

calendar AS (

    SELECT
        date,
        wm_yr_wk,
        weekday,
        wday,
        month,
        year,
        event_name_1,
        event_type_1,
        event_name_2,
        event_type_2,
        snap_CA,
        snap_TX,
        snap_WI
    FROM {{ ref('stg_calendar') }}

)

SELECT
    s.id,
    s.item_id,
    s.dept_id,
    s.cat_id,
    s.store_id,
    s.state_id,
    s.date,
    s.sales,
    c.wm_yr_wk,
    c.weekday,
    c.wday,
    c.month,
    c.year,
    c.event_name_1,
    c.event_type_1,
    c.event_name_2,
    c.event_type_2,
    c.snap_CA,
    c.snap_TX,
    c.snap_WI

FROM daily_sales AS s

LEFT JOIN calendar AS c
    ON s.date = c.date