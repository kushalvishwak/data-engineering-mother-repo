
with orders as (select * from {{ ref('stg_orders') }})

select
    order_key,

    customer_key,

    total_price

from orders

