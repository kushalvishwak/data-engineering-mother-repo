with customer as (
    select *
    from {{ source('source', 'customer') }}
)

select
    c_custkey as customer_key,
    c_name as customer_name,
    c_nationkey as nation_key
from customer

