-- Intermediate model: Customer Order Aggregations
with orders as (
    select * from {{ ref('stg_orders') }}
)

select
    customer_id,
    count(distinct order_id) as total_orders,
    count(distinct case when is_successful then order_id end) as successful_orders,
    min(order_date) as first_order_date,
    max(order_date) as latest_order_date,
    round(sum(case when is_successful then total_amount else 0 end)::numeric, 2) as lifetime_spend,
    round(avg(case when is_successful then total_amount end)::numeric, 2) as avg_order_value
from orders
group by customer_id
