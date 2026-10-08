# 04 · Data modeling

Model around business questions and declared grain. Document facts, dimensions, keys, time semantics, history policy, and ownership before choosing physical layout.

## SCD Type 1 and 2

Type 1 overwrites an attribute when history is not required. Type 2 preserves versions with effective start/end and current-row indicators. A robust Type 2 merge must handle duplicate source keys, out-of-order changes, unchanged attributes, and retries without creating duplicate versions.

Exercise: model subscriptions, plan changes, and daily recurring revenue. State the grain for each fact and explain how late-arriving corrections affect historical reporting.

## Temporal history example

[`examples/scd_type2.py`](examples/scd_type2.py) is a tested, pure-Python reference for ordered Type 2 updates with timezone-aware half-open validity intervals, duplicate-event handling, unchanged-attribute no-ops, and explicit rejection of overlapping or out-of-order changes. See `tests/` for executable invariants. It is an educational in-memory example, not a concurrent database merge implementation.
`