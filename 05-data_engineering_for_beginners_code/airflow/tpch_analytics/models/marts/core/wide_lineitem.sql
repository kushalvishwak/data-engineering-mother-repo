
With fct_lineitem As (
    Select *
    From
        {{ ref('fct_lineitem') }}
)

Select
    order_key,
    line_number
From fct_lineitem

