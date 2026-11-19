-- Staging model: Order Items
with source as (
    select * from {{ source('ecommerce_raw', 'order_items') }}
)

select
    order_item_id,
    order_id,
    product_id,
    quantity,
    round(unit_price::numeric, 2) as unit_price,
    round(discount::numeric, 2) as discount,
    round((quantity * unit_price - discount)::numeric, 2) as subtotal
from source
