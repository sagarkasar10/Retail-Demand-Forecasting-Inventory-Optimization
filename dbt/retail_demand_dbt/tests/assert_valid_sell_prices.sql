SELECT
    store_id,
    item_id,
    date,
    sell_price
FROM {{ ref('int_sales_with_prices') }}
WHERE sell_price IS NOT NULL
  AND sell_price < 0