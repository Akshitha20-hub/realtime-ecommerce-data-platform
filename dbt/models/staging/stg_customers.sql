-- Staging model: Customers
with source as (
    select * from {{ source('ecommerce_raw', 'customers') }}
)

select
    customer_id,
    trim(first_name) as first_name,
    trim(last_name) as last_name,
    trim(first_name) || ' ' || trim(last_name) as full_name,
    lower(trim(email)) as email,
    gender,
    age,
    trim(city) as city,
    trim(state) as state,
    signup_date::timestamp as signup_date,
    customer_segment
from source
