WITH store_data AS (

    SELECT DISTINCT
        store_id,
        state_id
    FROM {{ ref('stg_sales') }}

)

SELECT
    store_id,
    state_id

FROM store_data
WHERE store_id IS NOT NULL