# 03 · SQL

Practice readable, set-based SQL and reason about execution plans. Master joins, null semantics, CTEs, window functions, grouping sets, incremental predicates, transactions, and dialect differences.

## Advanced checklist

- Explain how join cardinality and filter selectivity affect a plan.
- Use `ROW_NUMBER` with a stable tie-breaker for deterministic deduplication.
- Distinguish event-time filtering from ingestion-time filtering in incremental loads.
- Review null behavior in anti-joins and `NOT IN`; prefer explicit semantics.

Exercise: calculate each customer's latest valid order and 90-day spend. Define how ties, cancellations, late corrections, and customers with no orders behave before writing the query.

## Worked query

[`examples/customer_order_analysis.sql`](examples/customer_order_analysis.sql) deduplicates by a stable source sequence, then computes a 90-day total while retaining customers with no qualifying orders. It uses named parameters and ANSI-style syntax; adapt interval and bind-parameter syntax to the target engine and verify the plan on representative data.
