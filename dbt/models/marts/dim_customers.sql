-- Mart: Customer Dimension (Enriched with Lifetime Value)
with customers as (
    select * from {{ ref('stg_customers') }}
),
customer_orders as (
    select * from {{ ref('int_customer_orders') }}
)

select
    customers.customer_id,
    customers.full_name,
    customers.email,
    customers.gender,
    customers.age,
    customers.city,
    customers.state,
    customers.signup_date,
    customers.customer_segment,
    coalesce(customer_orders.total_orders, 0) as total_orders,
    coalesce(customer_orders.successful_orders, 0) as successful_orders,
    customer_orders.first_order_date,
    customer_orders.latest_order_date,
    coalesce(customer_orders.lifetime_spend, 0) as lifetime_spend,
    coalesce(customer_orders.avg_order_value, 0) as avg_order_value,
    case
        when customer_orders.successful_orders > 1 then 'Repeat Buyer'
        when customer_orders.successful_orders = 1 then 'One-Time Buyer'
        else 'Non-Purchaser'
    end as buyer_type
from customers
left join customer_orders on customers.customer_id = customer_orders.customer_id
