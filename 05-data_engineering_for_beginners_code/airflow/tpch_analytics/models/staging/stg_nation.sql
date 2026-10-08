with nation as (
    select *
    from {{ source('source', 'nation') }}
)

select
    n_nationkey as nation_key,
    n_name as nation_name,
    n_comment as nation_comment,
    n_regionkey as region_key
from nation

