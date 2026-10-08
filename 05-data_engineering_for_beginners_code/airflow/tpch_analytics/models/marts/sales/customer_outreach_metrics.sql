
with wide_orders as (select * from {{ ref('wide_orders') }}),

order_lineitem_metrics as (select * from {{ ref('order_lineitem_metrics') }})

select
    wo.customer_key,
    wo.customer_name,
    MIN(wo.total_price) as min_order_value,
    MAX(wo.total_price) as max_order_value,
    AVG(wo.total_price) as avg_order_value,
    AVG(olm.num_lineitems) as avg_num_items_per_order
from wide_orders as wo
left join order_lineitem_metrics as olm on wo.order_key = olm.order_key
group by wo.customer_key, wo.customer_name

