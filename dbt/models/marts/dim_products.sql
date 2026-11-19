-- Mart: Product Dimension (Enriched with Sales Volume)
with products as (
    select * from {{ ref('stg_products') }}
),
items as (
    select * from {{ ref('stg_order_items') }}
)

select
    products.product_id,
    products.product_name,
    products.category,
    products.subcategory,
    products.price,
    products.cost,
    products.unit_margin,
    products.stock_quantity,
    products.product_rating,
    coalesce(sum(items.quantity), 0) as total_units_sold,
    coalesce(round(sum(items.subtotal)::numeric, 2), 0) as total_revenue_generated
from products
left join items on products.product_id = items.product_id
group by
    products.product_id,
    products.product_name,
    products.category,
    products.subcategory,
    products.price,
    products.cost,
    products.unit_margin,
    products.stock_quantity,
    products.product_rating
