WITH source_sales AS (

    SELECT *
    FROM {{ source('retail_demand', 'raw_sales') }}

)

SELECT *
FROM source_sales