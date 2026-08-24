WITH calendar_mapping AS (

    SELECT
        date,
        wm_yr_wk,
        ROW_NUMBER() OVER (
            ORDER BY date
        ) AS day_number
    FROM {{ ref('stg_calendar') }}

)

SELECT
    day_number,
    date,
    wm_yr_wk

FROM calendar_mapping