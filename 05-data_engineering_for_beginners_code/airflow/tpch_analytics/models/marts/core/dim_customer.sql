
with customer as (
    select *
    from {{ ref('stg_customer') }}
),

nation as (
    select *
    from {{ ref('stg_nation') }}
),

region as (
    select *
    from {{ ref('stg_region') }}
)

select
    c.customer_key,
    c.customer_name,
    n.nation_name,
    n.nation_comment,
    r.region_name,
    r.region_comment
from customer as c
left join nation as n on c.nation_key = n.nation_key
left join region as r on n.region_key = r.region_key

