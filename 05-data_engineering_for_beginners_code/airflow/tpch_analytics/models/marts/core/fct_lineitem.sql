
with stg_lineitem as (
    select
        order_key,
        line_number
    from {{ ref('stg_lineitem') }}
)

select
    order_key,
    line_number
from stg_lineitem

