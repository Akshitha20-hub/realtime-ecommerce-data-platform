-- Staging model: Events
with source as (
    select * from {{ source('ecommerce_raw', 'events') }}
)

select
    event_id,
    customer_id,
    product_id,
    lower(trim(event_type)) as event_type,
    event_timestamp::timestamp as event_timestamp,
    session_id
from source
