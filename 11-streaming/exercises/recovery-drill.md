# Structured Streaming recovery drill

Design a query that aggregates events into 10-minute event-time windows with a 20-minute late-data policy. Do not start with a product setting; first state what a consumer is allowed to see.

## Exercise

Document the following in a short recovery plan:

1. Event ID, event-time field, partition/order key, source retention, and duplicate policy.
2. Watermark meaning, late-event treatment, output mode, state growth, and any correction path.
3. Checkpoint location ownership, query identity, source offsets, and compatible restart procedure.
4. Sink commit/idempotency behavior if the process fails after the sink writes but before progress is recorded.
5. Recovery if checkpoint state is lost, including the maximum safe replay interval.
6. Metrics for source lag, event age, watermark delay, state size, rejected rows, and output reconciliation.

## Failure injection

Walk through a broker interruption, a sink timeout after a possible commit, a malformed event, checkpoint access loss, and a burst of late events. For each, distinguish automatic retry, operator action, and data correction. A watermark bounds state according to query semantics; it does not prove that no later event exists.
