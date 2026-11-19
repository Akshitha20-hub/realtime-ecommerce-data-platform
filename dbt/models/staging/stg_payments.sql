-- Staging model: Payments
with source as (
    select * from {{ source('ecommerce_raw', 'payments') }}
)

select
    payment_id,
    order_id,
    trim(payment_method) as payment_method,
    lower(trim(payment_status)) as payment_status,
    round(payment_amount::numeric, 2) as payment_amount,
    payment_date::timestamp as payment_date
from source
