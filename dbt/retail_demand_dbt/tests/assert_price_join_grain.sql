SELECT     
    item_id,     
    store_id,     
    date,     
    COUNT(*) AS record_count 
FROM {{ ref('int_sales_with_prices') }} 
GROUP BY     
    item_id,     
    store_id,     
    date 
HAVING COUNT(*) > 1 