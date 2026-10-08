select
    l_orderkey as order_key,
    l_linenumber as line_number
from {{ source('source', 'lineitem') }}

