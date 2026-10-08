# Snowflake interview practice

## How do micro-partitions and pruning affect performance?

**Short answer:** Snowflake stores data in micro-partitions with metadata that can eliminate irrelevant storage during scans.

**Deep explanation:** pruning depends on data distribution and predicates; clustering can affect locality, but maintenance has cost and is not automatically beneficial. Check query profile and representative workload before adding clustering keys or resizing warehouses.

**Example:** a time-filtered event table with naturally correlated load order may prune well without explicit clustering.

**Common mistake:** assuming a clustering key always speeds every query or treating warehouse size as a substitute for pruning.

**Senior follow-up:** what do you compare? Bytes scanned, partitions scanned, queue time, execution time, concurrency, credits, and freshness impact.

## Explain streams and tasks in incremental processing.

**Short answer:** streams expose change tracking and tasks schedule SQL work; together they can implement incremental transformations.

**Deep explanation:** track stream staleness/retention, transactional consumption, task dependencies, failure state, and idempotency. A stream is not an eternal change log. Plan reinitialization and reconciliation if the consumer falls outside retention.

**Example:** a task merges stream changes into a keyed target in a transaction, with monitoring for task failures and lag.

**Common mistake:** assuming a scheduled task's success guarantees the target is complete or that stream offsets can never expire.

**Senior follow-up:** how do you prevent cost surprises? Set warehouse sizing/autosuspend, monitor task/query history, isolate workloads, and alert on spend and backlog.
