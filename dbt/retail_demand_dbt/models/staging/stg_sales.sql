WITH source_sales AS (

    SELECT *
    FROM {{ source('retail_demand', 'raw_sales') }}

),

clean_sales AS (

    SELECT
        CAST(id AS STRING) AS id,
        CAST(item_id AS STRING) AS item_id,
        CAST(dept_id AS STRING) AS dept_id,
        CAST(cat_id AS STRING) AS cat_id,
        CAST(store_id AS STRING) AS store_id,
        CAST(state_id AS STRING) AS state_id,

        * EXCEPT (
            id,
            item_id,
            dept_id,
            cat_id,
            store_id,
            state_id
        )

    FROM source_sales

)

SELECT *
FROM clean_sales