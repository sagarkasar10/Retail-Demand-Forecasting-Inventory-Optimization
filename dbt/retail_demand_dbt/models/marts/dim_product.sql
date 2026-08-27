WITH product_data AS (

    SELECT DISTINCT
        item_id,
        dept_id,
        cat_id
    FROM {{ ref('stg_sales') }}

)

SELECT
    item_id,
    dept_id,
    cat_id

FROM product_data
WHERE item_id IS NOT NULL