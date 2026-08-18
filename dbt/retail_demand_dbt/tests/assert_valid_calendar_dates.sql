SELECT
    date
FROM {{ ref('stg_calendar') }}
WHERE date IS NULL