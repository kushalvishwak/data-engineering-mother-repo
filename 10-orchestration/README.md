# 10 · Orchestration

An orchestrator coordinates dependencies and state; transformation logic should remain testable outside it. Model schedules, event triggers, retries, deadlines, concurrency, backfills, sensors, and ownership explicitly.

Idempotency is an output property: rerunning a task for the same logical interval should not double-apply effects. Use bounded retries for transient faults, separate retryable from terminal errors, and make task boundaries align with recoverable units. Avoid using scheduler state as the only source of data truth.

Exercise: design a daily DAG with a late file, a downstream dimension update, and a failed quality gate. Explain backfill safety and how operators see the failed partition.
