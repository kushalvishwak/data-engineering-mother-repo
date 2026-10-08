
with fct_orders as (select * from {{ ref('fct_orders') }}),

dim_customer as (select * from {{ ref('dim_customer') }})

select
    f.order_key,
    f.total_price,
    d.customer_name,
    d.customer_key
from fct_orders as f
left join dim_customer as d on f.customer_key = d.customer_key

