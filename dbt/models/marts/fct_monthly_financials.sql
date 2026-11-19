-- Mart: Monthly Financial & Growth Metrics
with fct_orders as (
    select * from {{ ref('fct_orders') }}
    where is_successful = true
)

select
    order_year,
    order_month,
    count(distinct order_id) as total_orders,
    count(distinct customer_id) as active_customers,
    round(sum(total_amount)::numeric, 2) as gross_revenue,
    round(sum(total_discount)::numeric, 2) as total_discounts_given,
    round(sum(gross_profit)::numeric, 2) as net_profit,
    round((sum(gross_profit) / nullif(sum(total_amount), 0) * 100)::numeric, 2) as profit_margin_pct,
    round(avg(total_amount)::numeric, 2) as avg_order_value
from fct_orders
group by order_year, order_month
order by order_year, order_month
