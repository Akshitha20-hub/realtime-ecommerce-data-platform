-- Intermediate model: Order Margins & Line Item Economics
with items as (
    select * from {{ ref('stg_order_items') }}
),
products as (
    select * from {{ ref('stg_products') }}
)

select
    items.order_item_id,
    items.order_id,
    items.product_id,
    products.category,
    items.quantity,
    items.unit_price,
    items.discount,
    items.subtotal,
    products.cost,
    round((items.quantity * products.cost)::numeric, 2) as total_item_cost,
    round((items.subtotal - (items.quantity * products.cost))::numeric, 2) as gross_profit
from items
join products on items.product_id = products.product_id
