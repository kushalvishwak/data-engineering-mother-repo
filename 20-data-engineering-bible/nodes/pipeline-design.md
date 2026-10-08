---
id: pipeline-design
title: Pipeline Design
tier: 1
priority: must-know
sources: [obenner/system-design, obenner/cdc, obenner/data-quality, obenner/nifi, devinterview, cookbook]
---

# Pipeline Design

## Say it in one line
A production pipeline is a scheduled, idempotent, observable sequence of steps that lands data for consumers inside an agreed SLA and can be safely re-run over any past window.

## Must be able to recite
- **Idempotency** — Re-running a step with the same input leaves the same final result, so retries and backfills cannot double-count.
- **How you actually get it** — Deterministic keys with `MERGE`/upsert, or delete-then-insert of the whole partition being rewritten.
- **High-watermark** — The stored maximum `updated_at`, event time or log offset already processed, used to select the next incremental slice.
- **Event time vs ingestion time vs processing time** — When it happened, when you received it, when you computed on it; partition by event time or late rows land in the wrong day.
- **Late-arriving data** — Events that arrive after their partition or window closed; handle with a declared allowed lateness plus partition reprocessing.
- **Backfill** — Re-running history to fill or fix past partitions; it must be incremental, isolated from live reporting, and validated before consumers switch to it.
- **Retries with backoff** — Bounded automatic retries with growing waits, so a transient source or network failure never pages a human.
- **Dead-letter queue** — A side channel for records that fail parsing or validation, so one bad row neither stops the pipeline nor disappears silently.
- **Quarantine pattern** — Write rejected rows to a quarantine table with a reason, let good rows through, and alert on the rejection ratio.
- **Schema evolution policy** — Tolerate additive columns, fail fast on renames and type changes, and enforce the rule in CI or a schema registry.
- **Data contract** — An explicit producer/consumer agreement on schema, semantics, freshness and ownership, versioned as code and validated automatically.
- **SLA vs SLO** — The promise to consumers ("07:00 daily, complete") versus the internal target you monitor; freshness, completeness and failure rate are the metrics.
- **Checkpoint atomicity** — Commit the watermark/offset with the write, otherwise you get gaps (offset ahead of data) or duplicates (offset behind data).
- **Delivery semantics** — At-most-once loses, at-least-once duplicates, exactly-once in practice means at-least-once delivery plus an idempotent sink.
- **Separation of raw and derived** — Keep raw immutable and rebuild derived layers, because that is what makes a bug fix a re-run rather than a data-loss incident.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ How do you ensure idempotency in a data pipeline? — Write with deterministic keys (upsert/merge) or replace whole partitions, keep raw immutable and rebuild derived layers, and store checkpoints consistently with the writes.
- ★ What is the difference between at-most-once, at-least-once and exactly-once? — At-most-once may lose records, at-least-once may duplicate them on retry, exactly-once means neither and is normally achieved as at-least-once delivery plus idempotent or transactional writes.
- ★ How do you handle late-arriving events and backfills? — Define an allowed lateness, model tables by event time, reprocess the affected partitions or windows deterministically, and keep backfills isolated so live reporting is never half-updated.
- ★ How do you design for schema evolution and detect schema drift? — Version the contract, compare incoming schema to it on every load, allow additive columns by policy, and fail fast on renames or type changes before the data is corrupted.
- ★ Design an end-to-end batch analytics pipeline. — Immutable raw ingestion, curated cleaned/modelled layer, published marts for BI, with an SLA, quality checks and a named owner on each dataset, scheduled hourly or daily.
- ★ What are the common failure modes you have seen in pipelines? — Missing or partial partitions, duplicates from retries, schema drift and silent type coercion, time-zone and date-boundary bugs, and fan-out from an incorrect join.
- What are the main reliability patterns for pipelines? — Idempotent writes, retries with backoff, dead-letter queues, effectively-once processing, checkpoint/watermark discipline, and raw separated from derived.
- How would you design a near-real-time ingestion pipeline? — Read a CDC or event stream, append to a raw store with durable offsets, then materialise current-state tables and metrics with windowing and dedup, designing for replay, ordering and late events.
- ★ How do you model bronze/silver/gold layers and why? — Raw immutable, cleaned and standardised, business-ready; the split gives you reprocessing, clear contracts, and a place to put governance.
- What is a dead-letter queue and what goes into it? — A separate destination for records that cannot be parsed or that fail validation, so processing continues and the failures remain inspectable and replayable.
- How do you quarantine bad data without blocking the whole pipeline? — Route failing rows to a quarantine table with the reason, let valid rows continue, and alert when the quarantined share crosses a threshold.
- How do you design quality checks for an incremental pipeline? — Scope checks to the new slice (uniqueness on the batch keys, expected row-count bounds) and also assert full-table invariants and duplicate detection after the merge.
- What is data freshness and how do you measure it? — The gap between the newest event in a table and now; measured per table and alerted against the SLA, not eyeballed in the UI.
- What are data contracts? — Explicit, code-versioned agreements on schema, semantics, SLA and ownership between producer and consumer, enforced in CI so breaking changes fail before release.
- What is the difference between data validation and data reconciliation? — Validation asserts rules on a dataset (not null, unique, in range); reconciliation compares counts and totals between source and target to prove nothing was lost or duplicated.
- What is a watermark/offset and where should it be stored? — The position up to which input has been processed, stored durably by the ingestion tool and usually mirrored in a control table, updated atomically with the downstream write.
- What is the minimum set of checks you would put on every table? — Primary-key uniqueness, not-null on keys and critical measures, row-count bounds, and freshness.
- How do you test a data transformation? — Unit-test the logic on fixed input/expected-output fixtures, assert model tests in CI, and reconcile against the source on a known window.
- What is backpressure and what should a pipeline do about it? — When the consumer is slower than the producer, buffers fill and the system must slow the producer rather than drop data; NiFi does this by limiting connection queue size and pausing the upstream processor.
- How do you manage cost while still meeting SLAs? — Optimise storage layout and file sizes, avoid recomputing unchanged partitions, materialise selectively, schedule heavy jobs off-peak, and track cost per pipeline.
- How do you design observability for a data platform? — Monitor freshness, volume, quality and lineage plus runtime and failure rate, end to end from source to BI, with actionable alerts and runbooks.
- How do you design a platform used by several teams? — Isolate compute or apply quotas, assign dataset ownership, standardise naming/testing/docs, publish a catalogue, and cap cost so one team cannot starve another.
- What is an example of a serverless pipeline? — Object-storage arrival triggers a function or managed job, which writes to a managed warehouse or lake table, with the scheduler and scaling handled by the platform.
- Which systems in your stack provide transactions? — The OLTP source, the warehouse for its own DML, and ACID table formats in the lake; object storage alone and most stream sinks do not, which is why idempotency matters.
- What happens when the 03:00 job fails? — Retries with backoff fire first, then an alert with a runbook, and the fix is a re-run of the affected partition rather than a manual patch (not in sources, but standard).

## Traps
- Saying "we use `MERGE` so it is idempotent" without a deterministic latest-record rule; two updates for one key in the same batch make the result depend on row order.
- Treating a retry as free: a non-idempotent `INSERT` plus one retry is the single most common cause of duplicated facts.
- Partitioning by ingestion date and then being asked event-time questions; yesterday's numbers keep changing and you cannot explain why.
- Promising end-to-end exactly-once; interviewers want "at-least-once delivery plus idempotent writes", and they will push until they hear it.
- Backfilling straight into the live table — always write to a new partition or table and cut over after validation.
- Quoting an SLA you do not measure; if you cannot show freshness lag per table, you do not have an SLA, you have a hope.

## Graph
- **Needs first:** [[etl-vs-elt]]
- **Leads to:** [[orchestration-airflow]], [[data-quality]]
- **Asked together with:** [[system-design-scenarios]]
