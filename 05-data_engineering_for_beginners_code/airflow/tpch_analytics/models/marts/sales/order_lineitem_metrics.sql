
with wide_lineitem as (select * from {{ ref('wide_lineitem') }})

select
    order_key,
    COUNT(line_number) as num_lineitems
from wide_lineitem
group by order_key

