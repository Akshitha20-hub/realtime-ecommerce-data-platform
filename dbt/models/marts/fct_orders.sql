-- Mart: Core Orders Fact Table
with orders as (
    select * from {{ ref('stg_orders') }}
),
order_margins as (
    select
        order_id,
        count(order_item_id) as items_count,
        sum(quantity) as total_quantity,
        round(sum(discount)::numeric, 2) as total_discount,
        round(sum(gross_profit)::numeric, 2) as gross_profit
    from {{ ref('int_order_margins') }}
    group by order_id
),
payments as (
    select
        order_id,
        payment_method,
        payment_status
    from {{ ref('stg_payments') }}
)

select
    orders.order_id,
    orders.customer_id,
    orders.order_date,
    orders.order_day,
    orders.order_year,
    orders.order_month,
    orders.order_status,
    orders.shipping_city,
    orders.shipping_state,
    orders.total_amount,
    orders.is_successful,
    coalesce(order_margins.items_count, 0) as items_count,
    coalesce(order_margins.total_quantity, 0) as total_quantity,
    coalesce(order_margins.total_discount, 0) as total_discount,
    coalesce(order_margins.gross_profit, 0) as gross_profit,
    payments.payment_method,
    payments.payment_status
from orders
left join order_margins on orders.order_id = order_margins.order_id
left join payments on orders.order_id = payments.order_id
