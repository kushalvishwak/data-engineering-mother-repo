---
id: batch-vs-streaming
title: Batch vs Streaming
tier: 1
priority: must-know
sources: [obenner/flink, obenner/spark, obenner/system-design, obenner/nifi, obenner/cdc, cookbook]
---

# Batch vs Streaming

## Say it in one line
Batch processes a bounded dataset that is already complete, streaming processes an unbounded flow where completeness never arrives — so streaming trades correctness guarantees for latency and pays for it with time semantics, watermarks and state.

## Must be able to recite
- **Bounded vs unbounded** — Bounded data has a start and an end, so it can be sorted and processed once; unbounded data never ends, so every result is provisional.
- **Micro-batch** — Streaming implemented as a rapid sequence of small batches (Spark); simpler and cheaper than record-at-a-time, but it floors your minimum latency.
- **Event time, ingestion time, processing time** — When the event happened, when it entered the system, when the operator handled it; only event time gives reproducible results.
- **Watermark** — A declared bound on out-of-orderness ("nothing more than 2 minutes late"); a window fires once the watermark passes the window end.
- **Tumbling window** — Fixed size, no overlap, every event in exactly one window.
- **Sliding window** — Fixed size with a smaller slide, so windows overlap and one event contributes to several results.
- **Session window** — Variable length defined by an inactivity gap, closing when the user stops acting; used for activity and funnel analysis.
- **Count windows** — Fire on a number of records rather than on time, which is useful when volume matters more than clock.
- **Allowed lateness** — A grace period after the watermark during which a late event still updates its window; past that, it goes to a side output or a backfill.
- **At-most-once / at-least-once / exactly-once** — Loses records, duplicates records, or neither; exactly-once needs checkpointed state plus a transactional or idempotent sink.
- **Checkpoint and barrier** — A periodic consistent snapshot of operator state taken by flowing a barrier through the job; on failure the job restarts from the last checkpoint and replays the source.
- **Two-phase commit sink** — The sink pre-commits when the checkpoint snapshots and commits when the checkpoint is confirmed complete, which is how end-to-end exactly-once is reached.
- **Backpressure** — When a consumer is slower than its producer, the buffer fills and the slowdown propagates upstream instead of dropping data.
- **Stateful streaming** — Aggregations and joins keep keyed state in a state backend (memory, filesystem, RocksDB); state size, not throughput, is what usually kills these jobs.
- **Stream-stream joins** — Must be time-bounded (windowed or interval join) because neither side can be buffered forever.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ What is the difference between batch and stream processing? — Batch waits for a bounded dataset to be complete and then processes it; streaming processes an unbounded input continuously as records arrive, so results are emitted and revised over time.
- ★ How do you choose between batch and streaming? — From the latency the consumer actually needs: streaming buys freshness but adds state, ordering and exactly-once complexity, while batch is simpler and cheaper, and most real platforms stream into raw and batch into marts.
- ★ Tumbling vs sliding vs session windows? — Tumbling windows are fixed and non-overlapping, sliding windows are fixed but overlap because the slide is smaller than the size, session windows have no fixed size and close after an inactivity gap.
- ★ What is a watermark and how does it handle out-of-order data? — It is a declared maximum lateness that lets the engine decide a window is complete; with a 5-second window and 2-second watermark, the window closes when event time reaches 7 seconds.
- ★ What kinds of time exist in a streaming job? — Event time (when it happened), ingestion time (when it entered the engine) and processing time (when the operator saw it).
- ★ What is the difference between at-most-once, at-least-once and exactly-once? — At-most-once may lose data, at-least-once may duplicate it, exactly-once guarantees neither and requires checkpointing plus a transactional or idempotent sink.
- ★ What are micro-batches? — The input stream is cut into small batches processed by the batch engine, which is how Spark implements streaming, giving near-real-time rather than true record-at-a-time latency.
- ★ How do you handle late-arriving data? — Set the watermark to your real out-of-orderness, allow a lateness window for corrections, route later events to a side output or dead-letter path, and fix the rest with an event-time backfill of the affected partitions.
- What is bounded and unbounded data? — Bounded data has an end and can be fully sorted before computation; unbounded data has a beginning but no end, so it must be handled incrementally and ordering matters.
- How does a streaming job recover from a failure? — From its last checkpoint: state is restored and the source is rewound to the recorded offsets, so any record after the checkpoint is replayed.
- How does checkpointing actually work? — A barrier is injected at the source and flows through the operators; each operator snapshots its state when the barrier arrives, barriers are aligned at shuffles, and the job is durable once the sink confirms.
- How do you achieve exactly-once end to end? — Checkpointed operator state plus a two-phase-commit sink: pre-commit on snapshot, commit on checkpoint-complete notification, so a failed checkpoint rolls back cleanly.
- ★ What is the difference between Spark Streaming and Flink? — Spark treats streams as a series of small batches on its batch engine, Flink treats batch as a bounded stream on its streaming engine, so Flink gives lower latency and richer event-time and state handling.
- What is the difference between Kafka, Storm and Flink? — Kafka is the durable transport and buffer, Storm is a record-at-a-time compute engine, Flink is a stateful stream processor with event-time semantics that also runs batch.
- How does Spark Streaming work internally? — Incoming data is divided into small batches represented as a DStream, which is a sequence of RDDs, and normal transformations are applied per RDD (DStreams are legacy — Structured Streaming is the current API, so answer with both).
- What is Structured Streaming? — A fault-tolerant stream-processing engine on the Spark SQL engine where you express streaming aggregations and event-time windows with the DataFrame/Dataset API.
- What is the significance of a sliding window operation? — Transformations are applied over a window of data that advances by a slide interval, so each output covers overlapping input and you get rolling metrics such as "last 5 minutes".
- Where is streaming state stored? — In a state backend: memory for tests, filesystem for moderate state, RocksDB on local disk for large keyed state that will not fit in heap.
- How do you enrich a stream with a dimension table? — Broadcast or cache small dimensions in operator state, use async lookups against an external store for large ones, and use a temporal/versioned join when the dimension itself changes.
- How do you join two streams where one side arrives late? — With an interval join bounded by event time and watermarks, giving each side an offset range instead of waiting indefinitely.
- What do you do about data skew in a streaming job? — Find the hot key, then salt it or pre-aggregate locally before the keyed shuffle; adding parallelism alone leaves the extra tasks idle.
- What is backpressure and what should happen? — The producer is faster than the consumer, so queues fill; a correct system limits the queue and slows the producer instead of dropping records, as NiFi does with connection backpressure thresholds.
- How do you handle abnormal or malformed records in a stream? — Validate on ingest, repair what is deterministically repairable, route the rest to a side output or quarantine, and report the rate rather than dropping them silently.
- Why do checkpoints time out and how do you fix it? — Usually huge state, a slow sink or barrier alignment behind backpressure; fix the bottleneck, use incremental or unaligned checkpointing, and increase the interval rather than the timeout alone.
- Is data loss possible in a streaming engine? — Yes with at-most-once settings or a non-replayable source; with checkpointing, replayable sources and idempotent sinks you get at-least-once or exactly-once (the source claims at-most-once is no longer available in newer Flink; more precisely, at-most-once is not a checkpointing mode — it is what you get with checkpointing disabled).
- When do you use incremental aggregation instead of a full window function? — Incremental aggregation keeps one accumulator per window and is what you want for sums and counts; a full-window function buffers every record and is only worth it for things like sorting or top-N inside the window.

## Traps
- Saying "streaming is real-time, batch is legacy"; the interviewer wants the cost and complexity trade-off, and the fact that most platforms are hybrid.
- Confusing a streaming watermark (an event-time completeness bound) with a batch high-watermark (the last offset or timestamp processed).
- Claiming exactly-once from the framework alone; without a transactional or idempotent sink you have at-least-once, whatever the config says.
- Using processing time for windowed aggregates and then being unable to explain why a replay produces different numbers.
- Answering backpressure with "increase parallelism" before checking skew and sink latency.
- Treating micro-batch as identical to record-at-a-time; the batch interval is a hard floor on latency, which matters when the SLA is sub-second.

## Graph
- **Needs first:** [[pipeline-design]]
- **Leads to:** [[kafka-messaging]], [[lambda-kappa]]
- **Asked together with:** [[spark-core]]
