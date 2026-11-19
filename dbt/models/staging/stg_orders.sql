-- Staging model: Orders
with source as (
    select * from {{ source('ecommerce_raw', 'orders') }}
)

select
    order_id,
    customer_id,
    order_date::timestamp as order_date,
    date_trunc('day', order_date::timestamp) as order_day,
    extract(year from order_date::timestamp)::integer as order_year,
    extract(month from order_date::timestamp)::integer as order_month,
    lower(trim(order_status)) as order_status,
    trim(shipping_city) as shipping_city,
    trim(shipping_state) as shipping_state,
    trim(payment_method) as payment_method,
    round(total_amount::numeric, 2) as total_amount,
    case when lower(order_status) in ('completed', 'shipped') then true else false end as is_successful
from source
