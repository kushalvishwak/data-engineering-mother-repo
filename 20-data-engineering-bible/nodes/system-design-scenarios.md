---
id: system-design-scenarios
title: System Design Scenarios
tier: 3
priority: must-know
sources: [obenner/system-design.md, obenner/data-quality.md, obenner/observability.md, obenner/cost-optimization.md, obenner/data-governance.md, devinterview, cookbook]
---

# System Design Scenarios

## Say it in one line
A scenario answer is a fixed walk — clarify the requirement, get volumes and SLAs, fix the grain, then ingestion, storage, processing, serving, quality, cost, failure modes — with the trade-off you accepted said out loud at every box.

## Must be able to recite
- **The framework** — clarify requirements → volumes and SLAs → grain and schema → ingestion → storage → processing → serving → quality → cost → failure modes → trade-offs stated out loud; say the sequence first, then walk it, so the interviewer knows where you are.
- **Clarify before designing** — three questions buy you the whole design: who consumes this and how stale can it be, can the source give me changes only or must I read it all, and what happens if a record is late or lost.
- **Numbers before tools** — rows per day times bytes per row gives GB per day and GB per year, then peak versus average, then the deadline in minutes; a design with no number is an opinion, and 2 GB a day does not need a cluster.
- **Fix the grain out loud** — say "one row per X" before choosing anything, because the partition key, the dedup key, the SCD type and every aggregate fall out of the grain.
- **Land raw immutable** — bronze keeps source bytes plus ingest metadata, silver is cleaned, deduplicated and conformed, gold is the mart; the point is that silver and gold can be rebuilt without re-reading the source.
- **Idempotency by default** — `MERGE` on a deterministic key, or delete-and-reinsert the whole partition, so a rerun produces the same table; retries are certain, so design for them rather than reacting to them.
- **Delivery semantics** — at-most-once loses records, at-least-once duplicates them, exactly-once needs a transactional sink or deduplication on a key; the defensible answer is at-least-once plus an idempotent write, which is effectively-once.
- **Event time and allowed lateness** — model by event time, declare how late is still accepted (say seven days), and reprocess the affected partitions when a late batch arrives rather than appending it to today.
- **Partitioning and file size** — partition on the column consumers filter (usually a business date), target files in the hundreds of MB, and refuse high-cardinality partition keys that shatter the table into small files.
- **Failure modes to volunteer** — upstream outage or late data, schema change, duplicates from a retry, skew and stragglers, a partial write, a timezone or partition-boundary bug, and a cost spike.
- **Reliability toolkit** — retries with backoff, dead-letter queue for rejects, checkpoint or offset committed with the write, staged write then atomic publish, and replay from immutable raw.
- **Batch until proven otherwise** — choose streaming only when a named decision needs sub-minute data, because streaming buys latency and pays in state, ordering, replay and on-call complexity.
- **Cost levers in order** — partition pruning, column pruning with a columnar format, incremental instead of full reload, compaction of small files, materialise only expensive results that are reused, off-peak scheduling, quotas on shared compute.
- **Say the trade-off** — every box gets one sentence: "I chose A over B because <requirement>, and the cost is <downside>"; the trade-off sentence is what is being scored, not the tool name.
- **Draw four boxes** — source → ingest/raw → transform/model → serve, with the quality gate before publish and the orchestrator across the top; the picture stops you rambling and shows where the SLA is measured.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ How would you design an end-to-end batch pipeline? Concretely: a daily load from an OLTP orders database into the warehouse. — Read from a replica not the primary, pull changes only (an `updated_at` watermark or CDC) → land raw partitioned by load date → stage and deduplicate on the business key keeping the latest version → `MERGE` into dimensions (SCD2 where history is needed) and append to the fact → run uniqueness, not-null, referential and reconciliation tests → publish; state the grain and the landing deadline before naming a tool, and give every dataset an SLA, a check and an owner.
- Design a fact table for transactions. — Grain is one row per transaction (or per leg); surrogate foreign keys to account, customer, merchant and date dimensions, the transaction id kept as a degenerate dimension, additive measures only (amount, fee, count), partitioned by transaction date, amounts stored in minor units with a currency code; a correction arrives as a reversal row, never as an update.
- ★ How would you design a near-real-time pipeline? Concretely: the business wants a dashboard no more than two minutes stale. — First ask which decision needs two minutes; if it is real, CDC or events → Kafka with durable offsets → stream job writing an append-only raw table plus an upserted current-state table → BI reads a small pre-aggregated table, not raw; design explicitly for replay, out-of-order arrival and late events, and keep the nightly batch as the correctness backstop that you reconcile against daily.
- ★ Your stream delivers at-least-once and you must not double-count. — Deduplicate on a producer-supplied event id, either in a windowed state store or with `row_number() over (partition by event_id order by ingest_time)` over the raw table, then `MERGE` into the target so a replay is a no-op; state the dedup window and what you do with a duplicate that arrives after it.
- ★ Design a pipeline that must never lose a record (payments). — Durable log with offsets committed only after the write, at-least-once delivery plus an idempotent `MERGE` on transaction id, a dead-letter queue that alerts and can be replayed, immutable raw so any layer can be rebuilt, and a daily reconciliation of count and sum against the source of record producing a break report.
- ★ Volumes are going 5x next quarter — what breaks and what do you change? — Name the bottleneck first (source extract, scan volume, shuffle, warehouse concurrency), then in order: full reload becomes incremental, fix partitioning and file sizes, push filters and columns down, parallelise the extract by key range, scale out or isolate the heavy workload; say which parts scale linearly and re-quote the SLA under the new volume.
- Backfill three years of history. — Run it as a separate throttled job, chunked by month, writing to a shadow table while the daily pipeline keeps running, validate each chunk against a control total, then swap or publish; estimate cost and runtime by measuring one chunk and extrapolating, and warn consumers that historical metrics will move.
- An upstream team changes the schema without telling you. — Validate every batch against the contract (columns, types, nullability), allow additive columns, fail fast on rename or type narrowing, quarantine the offending batch instead of corrupting the target; then fix the process with a producer-side CI check and a schema registry compatibility rule.
- ★ A dashboard query that took three seconds now takes three minutes. — Reproduce it and read the plan; the usual causes are a lost partition filter, a fan-out join, small files or no partitioning, `select *`, views stacked on views, and no pre-aggregation — fix in that order and materialise the aggregate at the grain the dashboard actually displays.
- ★ A customer asks to be deleted and their data is across the lake. — Use lineage to list every dataset holding their identifier, then either delete rows in a table format that supports row-level deletes and expire the old snapshots, or crypto-shred by dropping that subject's key; design for it up front by keeping personal data in one keyed vault table, and do not forget backups, dead-letter queues, extracts and lower environments.
- Design a platform several teams share. — Isolation with separate compute or quotas so one bad query cannot starve others, one named owner per dataset, shared naming, testing and documentation standards, a catalogue for discovery, and cost attribution per team.
- How do you choose the right storage for different consumers? — Map each consumer to its access pattern: aggregate scans for BI to a columnar warehouse or lakehouse table, single-key application lookups to a key-value or document store, exploration to lake tables with an engine over them, sub-second serving to a cache or precomputed table; duplicating data deliberately is fine as long as you name the source of truth.
- ★ How do you ensure idempotency in a pipeline? — Write with deterministic keys through upsert or merge, or replace a whole partition; keep raw immutable and rebuild derived layers, and commit checkpoints or watermarks in the same step as the write.
- How do you handle late-arriving events and backfills? — Table designed by event time, a declared allowed lateness, reprocessing of the affected windows deterministically, and backfills that are incremental, validated and isolated from current reporting.
- ★ When do you choose streaming over batch? — Streaming when the consumer decision needs low latency and continuous updates, batch when the data is consumed on a schedule; most real systems are hybrid, streaming into raw and batch into marts.
- Explain bronze, silver and gold layers. — Bronze is immutable ingestion with no business logic, silver is cleaned, standardised and deduplicated with a stable schema, gold is business-ready marts and aggregates; the layering is what makes reprocessing and contracts possible.
- How do you design for schema evolution? — Version the contract, define compatibility rules, enforce them in CI and at ingest, tolerate additive fields downstream, fail fast on breaking changes, and keep outputs backward compatible while several consumers depend on them.
- What are the reliability patterns for pipelines? — Idempotent writes, retries with backoff, dead-letter queues, effectively-once processing, separation of raw from derived, checkpointing, and consistent watermark management to avoid both gaps and duplicates.
- ★ What is the difference between at-most-once, at-least-once and exactly-once? — At-most-once may drop on failure, at-least-once may redeliver, exactly-once requires transactional coordination or a dedup key; in analytics you almost always build at-least-once plus idempotent writes.
- ★ Full load or incremental load — which do you pick? — Full when there is no reliable change marker or when the source is small enough that simplicity wins, incremental when volume makes reloading wasteful; incremental needs a watermark, dedup and completeness checks in exchange.
- ★ Why have a staging layer at all? — It separates extract from transform so you can validate, clean and deduplicate before touching the target, re-run the transform without hitting the source again, and recover from a failed load.
- Lambda versus kappa architecture, and can you keep the two layers in sync? — Lambda runs a batch layer and a speed layer and merges them at serving, kappa keeps one streaming path and replays the log to recompute; you keep lambda in sync by making both paths read the same immutable log and by reconciling the batch result over the streaming result for closed periods.
- How do you meet an SLA and control cost at the same time? — Optimise layout (partitioning, file sizes) and avoid recomputation, materialise selectively, schedule heavy work off-peak, enforce quotas, and track cost per pipeline so a regression is visible.
- ★ How would you handle a sudden 10x spike in incoming volume? — Buffer in a queue so the spike does not reach the database, autoscale or use serverless compute for the burst, process in parallel by partition key, and shed or delay non-critical work; the queue is what turns a spike into a latency problem instead of an outage.
- What factors decide which database you pick? — Access pattern and query shape, consistency requirement (CAP: under a partition you keep either availability or consistency), write and read volume, latency target, and operational cost; say the pattern first and the product second.
- What does a serverless pipeline look like? — Object storage event triggers a function or a managed job, which lands the file into a table and calls the transform; cheap and elastic for spiky low-volume feeds, but you pay in cold starts, timeouts and harder local testing.
- How would you design observability for what you just drew? — Freshness, volume, quality and lineage per dataset plus run status and duration per job, alerting on the consumer-visible breach with a runbook and an owner.

## Traps
- Naming tools before requirements — "Kafka and Spark" for a 2 GB daily feed is a fail; ask volumes and freshness first and be willing to say a scheduled SQL job is enough.
- Never stating the grain — the design becomes unfalsifiable, and every later answer (dedup key, partition, aggregate) has nothing to hang on.
- Promising exactly-once — say at-least-once with idempotent writes and dedup on a key; at a bank this is exactly where the follow-up question lands.
- Designing only the happy path — volunteer three failure modes and their handling before being asked, because that is the part that separates candidates.
- Leaving trade-offs silent — if you do not say what you gave up, the interviewer assumes you did not know there was a choice.
- Forgetting operations — no SLA, no owner, no runbook, no backfill path and no cost estimate means you designed a diagram, not a system.

## Graph
- **Needs first:** [[warehouse-architecture]], [[pipeline-design]], [[batch-vs-streaming]]
- **Leads to:** [[behavioral-project-story]]
- **Asked together with:** [[nosql-stores]], [[lambda-kappa]]
