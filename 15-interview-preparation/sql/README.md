# SQL interview practice

## How do you deduplicate to the latest row per key?

**Short answer:** rank rows per business key using a deterministic ordering, then select rank one.

**Deep explanation:** the ordering needs source sequence or another stable tie-breaker; event time alone can tie. Define how null keys and deletes behave. Validate uniqueness after the transformation and inspect the query plan at scale.

**Example:** `ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY source_version DESC, ingest_id DESC)` and filter `rn = 1`.

**Common mistake:** using `MAX(updated_at)` and joining back when multiple rows share the maximum timestamp.

**Senior follow-up:** how do you handle late corrections? Preserve source ordering/history or recompute the affected key/partition; do not treat ingestion time as business order.

## Why can `NOT IN` behave unexpectedly with NULL?

**Short answer:** a NULL in the subquery can make comparisons unknown, so rows may not pass the filter.

**Deep explanation:** SQL uses three-valued logic. Choose an explicit null policy and use `NOT EXISTS` or a null-filtered anti-join when that matches the intended semantics. Check engine-specific optimizer behavior and key nullability.

**Example:** use `WHERE NOT EXISTS (SELECT 1 FROM blocked b WHERE b.id = source.id)` and decide separately whether `source.id IS NULL` is retained.

**Common mistake:** assuming NULL equals NULL or that `NOT IN` is always a safe anti-join.

**Senior follow-up:** how would you detect a cardinality regression? Compare expected grain, uniqueness, row counts, and plan estimates to observed metrics.
