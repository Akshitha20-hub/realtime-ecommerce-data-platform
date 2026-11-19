-- Staging model: Products
with source as (
    select * from {{ source('ecommerce_raw', 'products') }}
)

select
    product_id,
    trim(product_name) as product_name,
    trim(category) as category,
    trim(subcategory) as subcategory,
    round(price::numeric, 2) as price,
    round(cost::numeric, 2) as cost,
    round((price - cost)::numeric, 2) as unit_margin,
    stock_quantity,
    round(product_rating::numeric, 2) as product_rating
from source
