# Reliability basics

State explicitly what a successful run guarantees. A useful pipeline contract names its input snapshot or offset range, output dataset and partition, schema version, quality checks, and commit marker. A retry must either produce the same logical result or detect that the result was already committed.

Classify failures: transient dependency issue, bad input, code defect, capacity exhaustion, or authorization/configuration. Retry only failures likely to recover; use bounded exponential backoff with jitter for transient errors. Route deterministic bad records to a quarantine path with reason and source identity.

Measure freshness, volume, schema drift, error rate, and end-to-end success. An alert should identify an owner and an action. A green scheduler status alone does not prove data correctness.
