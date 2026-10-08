# Example contract: daily orders

- Grain: one source order change event; key: `(source_system, order_id, source_version)`.
- Event time: source `updated_at` in UTC; ingestion time recorded separately.
- Delivery: at least once; consumers deduplicate by key and version.
- Completeness: publish only after the source manifest is present and row count is reconciled.
- Late data: accept corrections for seven days; rerun affected event-date partitions.
- Sensitive fields: customer email restricted to approved roles; never log payloads.
- Recovery: replay a bounded source interval; output writes are idempotent.
