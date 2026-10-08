---
id: lambda-kappa
title: Lambda vs Kappa Architecture
tier: 1
priority: should-know
sources: [obenner/flink, obenner/kafka, obenner/system-design, obenner/hudi, obenner/iceberg, obenner/dwha, cookbook]
---

# Lambda vs Kappa Architecture

## Say it in one line
Lambda runs a batch layer and a streaming layer over the same events and merges them at query time; Kappa deletes the batch layer and reprocesses history by replaying the retained log through the same streaming code.

## Must be able to recite
- **Lambda's three layers** — Batch layer recomputes from the immutable master dataset, speed layer covers recent events approximately, serving layer merges both for the query.
- **Why Lambda existed** — Early stream engines could neither guarantee exactly-once nor reprocess history, so a nightly batch recomputation had to be the source of truth.
- **Lambda's real cost** — The same business logic lives twice in two engines, so the two implementations drift and every metric change is two changes.
- **Kappa** — A single streaming pipeline where "batch" is just replaying the log from the earliest offset into a new version of the job.
- **Reprocessing in Kappa** — Start a second job from offset zero writing to a new table, let it catch up, validate, then switch consumers and drop the old output.
- **What Kappa requires** — A durable replayable log (long Kafka retention or tiered storage), event-time processing, and idempotent or transactional sinks.
- **Serving-layer merge** — Read the batch view for closed periods and the speed view for the open period, deduplicating on key so the overlap is not counted twice.
- **Speed layer is provisional** — Recent numbers may be approximate and get corrected when the batch layer catches up, and consumers must be told which they are seeing.
- **When Lambda is still right** — Batch-only sources, heavy historical joins, or regulatory recomputation from raw where the recompute must be provably independent.
- **When Kappa is right** — Sources already on an event log, one team owning the logic, and a latency requirement below any batch cadence.
- **The hybrid everyone actually runs** — Stream into an immutable raw layer, then batch or incrementally model into marts, which gives streaming freshness with batch reproducibility.
- **Lakehouse convergence** — ACID table formats (Iceberg, Hudi, Delta) let one table be written by streaming and read by batch, removing much of Lambda's original justification.
- **Choose from the SLA, not the tooling** — The tolerated staleness of the consumer decides the architecture; everything else is implementation detail.
- **Keeping the layers reconcilable** — Same event-time partitioning, same keys and one shared transformation library, or the merge can never be proven correct.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- Can you sync the batch and streaming layers, and if so how? — Yes: derive both from the same immutable event log, partition and key both outputs by event time and entity id, share one transformation library, and let the batch view overwrite the speed view for periods it has covered.
- ★ What is the difference between Lambda and Kappa architecture? — Lambda keeps separate batch and speed layers merged by a serving layer; Kappa keeps only the stream and replays the retained log to recompute history, so there is one codebase instead of two.
- ★ What is streaming and what is batching? — Batching processes a bounded, already-complete dataset on a schedule; streaming processes an unbounded flow continuously as events arrive.
- ★ What is the upside of streaming over batching? — Fresh results and continuous incremental updates instead of waiting for a cycle boundary, at the cost of state management, ordering and exactly-once complexity.
- ★ How do you choose between the two for a new use case? — Start from the consumer's tolerated staleness and the cost ceiling; streaming for genuinely sub-cycle latency, batch when hourly or daily is enough, hybrid when the same events feed both a dashboard and a report.
- ★ How do you reprocess a year of history in a Kappa setup? — Replay from the earliest retained offset into a new output table with a new job version, keep the current one serving, then cut over after reconciling the two.
- What does Kappa require from your message broker? — Retention long enough (or tiered storage) to replay the whole history, stable partition keys for ordering, and consumer offsets you can reset.
- Which layer serves a query, and what happens when the two disagree? — The serving layer merges them, treating the batch view as authoritative for closed periods and the speed view as provisional for the current one; a persistent disagreement means the two implementations have drifted.
- Design a system that gives a live dashboard and a nightly regulatory report from the same events. — One ingestion path into an immutable raw event log, a streaming job maintaining the dashboard's current-state tables, and a batch job recomputing the certified report from the same raw data with its own quality gates.
- ★ How do you handle an event that arrives after the batch layer already published? — Reprocess the affected event-time partition and republish it deterministically, which is why partitions must be rewritable and reports must record which version they were built from.
- Why is Lambda architecture criticised? — Two engines, two codebases and two sets of bugs for a single metric, plus a serving layer whose merge logic is itself a source of error.
- ★ What are microbatches, and do they make Lambda unnecessary? — Microbatching cuts a stream into small batches processed by the batch engine; it narrows the latency gap but does not by itself give you replayable history, which is what actually removes the batch layer.
- What is the master dataset and why must it be immutable? — It is the append-only raw event store the batch layer recomputes from; if it can be edited you lose the ability to prove any published number.
- How does a lakehouse table format change this decision? — Snapshot isolation, upserts and time travel let streaming and batch write and read one table, so you keep a single physical dataset instead of separate batch and speed stores.
- Can Flink replace Spark's batch processing so you only need one engine? — That is the goal of treating batch as a bounded stream, and Flink can do it, but Spark still outperforms it on large batch workloads, so most shops keep both.
- What is the difference between Kafka, Storm and Flink in this architecture? — Kafka is the replayable log both layers read, Storm or Flink is the speed layer, and Flink can also be the batch layer if you commit to Kappa.
- What is real-time data warehousing? — The warehouse captures business activity as it completes rather than on a nightly cycle, so the activity is queryable almost immediately.
- Where does the serving layer live in practice? — In the warehouse or a serving store: batch-built marts for closed periods plus a streaming-maintained current-state table, exposed to BI as one view.

## Traps
- Reciting the three layers without naming the actual pain — two codebases for one metric is the whole point of the question.
- Saying "Kappa is just streaming"; the defining property is replay of a retained log, so without long retention or tiered storage you cannot reprocess and it is not Kappa.
- Assuming Kappa removes the need for an immutable raw layer; the raw events still exist, they just live in the log or lake instead of a batch store.
- Merging batch and speed views without event-time keys and deduplication, so the overlapping period is double counted.
- Calling Lambda obsolete in a bank interview — regulatory recomputation from raw is exactly the batch layer, and it is not going anywhere.
- Choosing the architecture from the tools on offer rather than from the freshness the consumer actually needs.

## Graph
- **Needs first:** [[batch-vs-streaming]], [[kafka-messaging]]
- **Leads to:** [[system-design-scenarios]]
- **Asked together with:** [[warehouse-architecture]]
