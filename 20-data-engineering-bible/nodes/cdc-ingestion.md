---
id: cdc-ingestion
title: Change Data Capture (CDC)
tier: 1
priority: should-know
sources: [obenner/cdc, obenner/hudi, obenner/dwha, obenner/system-design, devinterview]
---

# Change Data Capture (CDC)

## Say it in one line
CDC captures every row-level insert, update and delete at the source — normally by reading the database's transaction log — and streams those changes downstream instead of rescanning whole tables.

## Must be able to recite
- **Log-based CDC** — Reads the WAL, binlog or redo log directly: lowest source overhead, sees deletes, but needs replication privileges and careful offset handling.
- **Query-based CDC** — Polls `WHERE updated_at > watermark`: trivial to build, but misses hard deletes and any change that does not move the timestamp.
- **Trigger-based CDC** — Triggers write changes into a shadow table: works without log access, adds write latency to OLTP and breaks on DDL changes.
- **Debezium** — The standard open-source log-based connector set for MySQL, Postgres, SQL Server, Oracle and Mongo, usually run on Kafka Connect.
- **Snapshot then stream** — An initial consistent snapshot bootstraps existing rows, then incremental streaming continues from the log position where the snapshot ended.
- **Offset / LSN** — The source log position processed so far, stored durably and committed together with the downstream write.
- **Tombstone** — A record carrying a key with a null value to mark a delete; compacted topics and upsert sinks use it to actually remove the key.
- **Before and after image** — The old and new values in a change event; without a full after-image you must reconstruct the row from previous state.
- **Per-key ordering** — Global ordering is not achievable across partitions, so key by primary key and order within the key by LSN or transaction id.
- **Idempotent apply** — Upsert on the primary key keeping the highest LSN or `updated_at`, so replays and duplicate deliveries converge to the same state.
- **Soft vs hard delete** — Keep `is_deleted`/`deleted_at` for audit and analytics, or physically remove the row; regulated environments usually want soft delete plus retained history.
- **CDC feeding SCD2** — Each change event closes the current version (`valid_to`, `is_current = false`) and inserts a new row, which is exactly a Type 2 dimension.
- **Outbox pattern** — The application writes its event into an outbox table in the same transaction as the business row and CDC publishes it, which removes the dual-write problem.
- **CDC lag** — Source LSN minus processed LSN plus target freshness; it comes from source write bursts, connector stalls, partition hotspots or slow downstream merges.
- **Log retention risk** — If the source recycles its log before the connector catches up, the only recovery is a fresh snapshot.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ What is CDC and how does it work? — It captures row-level inserts, updates and deletes from a source, usually by reading the transaction log, and streams them downstream as an append-only change log plus a materialised current-state table.
- ★ How do you make CDC ingestion idempotent? — Use a stable key (primary key plus source LSN or transaction id), apply deterministic upsert/merge logic, and land raw changes append-only so current state can be rebuilt as "latest per key".
- ★ How do you handle schema evolution in a CDC pipeline? — Allow additive columns, fail fast and alert on renames and type changes, enforce compatibility with a schema registry and CI, and make downstream tables tolerant of extra fields.
- ★ What delivery semantics exist, and which do you actually get? — At-most-once loses, at-least-once duplicates, exactly-once is hard end to end; production systems deliver "effectively once" by combining at-least-once with idempotent writes and deterministic merges.
- ★ When would you choose CDC over batch ingestion? — When you need low latency, continuous incremental processing or a trustworthy change history, or when the table is too large or too hot for repeated full scans; batch stays simpler when latency is relaxed.
- ★ How does CDC feed an SCD Type 2 dimension? — Order the change events per key, close the current row's validity window and insert a new version for each tracked-column change, so the dimension carries full history.
- ★ How do you design a safe backfill or reprocessing strategy? — Keep the raw change log immutable and rebuild derived tables from it, run the rebuild into a new table or snapshot, validate it, then switch consumers.
- ★ What are the most common failure modes in CDC pipelines? — Duplicates from retries and rebalances, missed events from offset mismanagement or expired log retention, schema drift, wrong delete handling, and out-of-order application of updates.
- What are the trade-offs between log-based, trigger-based and timestamp-based CDC? — Logs give high fidelity at low source cost but need privileges; triggers work without log access but slow writes and break easily; timestamps are simple but miss deletes and can duplicate.
- What is the difference between snapshot and incremental CDC? — The snapshot reads a consistent baseline of existing rows; incremental streams changes after that baseline from a log offset, and most systems need both.
- How do you handle deletes? — Apply hard deletes, apply soft deletes with a flag and timestamp, or keep the append-only history and compute current state with delete logic; the choice follows compliance and consumer needs.
- What is ordering, and why is it hard in CDC? — Ordering means applying changes in source order; partitioning, retries and parallel delivery break it, so correctness relies on per-key or per-partition order using source transaction metadata.
- What is a watermark/offset, and where should it be stored? — The position up to which changes are processed, stored durably in the connector state and usually mirrored in a control table, updated atomically with the downstream write.
- How do you handle updates when the source only emits changed columns? — Reconstruct the full row by joining against previous state, or configure the connector to emit before/after images; either way you must handle out-of-order updates.
- What is the outbox pattern and why is it useful? — Business events are written to an outbox table inside the same transaction as the data change and published by CDC, so the database write and the event publish cannot diverge.
- How do you monitor CDC lag, and where does lag come from? — Compare source LSN with processed LSN, watch consumer offsets and target freshness; lag originates in source write bursts, connector slowness, broker throughput or hotspots, and slow downstream merges.
- How do you apply CDC into a lakehouse table? — Ingest the events as upserts and deletes keyed by a record key with a precombine field to pick the latest, keep an append-only log beside the current-state table, and monitor compaction backlog.
- What are a record key and a precombine field, and why do you need both? — The record key identifies the row, and the precombine field (for example `updated_at`) resolves several events for the same key in one batch so the upsert is deterministic.
- Is CDC or a full reload faster for a 500-million-row table with 1% daily change? — CDC, because full reload cost scales with table size while CDC scales with the change volume; the full reload only wins when the source has no reliable change signal.
- What happens if the connector is down for two days? — It resumes from its stored offset if the source log still holds that position; if retention has passed it, you must re-snapshot, which is why log retention must exceed your worst outage.
- Where do you store the raw change events, and why keep them? — In an immutable append-only raw layer, because every derived current-state table and mart can then be rebuilt after a logic bug without touching the source.
- Can you run CDC against a source where you have no admin rights? — Not log-based; without replication privileges you fall back to trigger-based or timestamp polling, and you lose delete detection.
- What is Debezium and what does it need on the database side? — A log-based CDC connector suite normally deployed on Kafka Connect; it needs logical replication or binlog access, row-level logging, and a replication user (not in sources, but standard).
- What is the difference between CDC and database replication? — Replication rebuilds an identical copy for availability, CDC turns the same log into consumable business events that can be reshaped and fanned out (not in sources, but standard).

## Traps
- Offering `updated_at` polling as "CDC" without the caveats; it cannot see deletes and misses rows updated inside the same timestamp granularity.
- Assuming the transport gives global ordering; with Kafka you only get order inside a partition, so keying by primary key is what preserves per-row order.
- Applying events in arrival order instead of by LSN, which lets a retried old update overwrite a newer value.
- Committing offsets before the downstream write succeeds, which loses events with no error anywhere.
- Treating the initial snapshot as free; on a large table it scans for hours, can hold locks, and may outlive the source's log retention if not chunked.
- Ignoring tombstones when the target is a compacted topic or an upsert table, so deletes never propagate and the row lives forever.

## Graph
- **Needs first:** [[sql-ddl-dml-transactions]], [[scd-history]]
- **Leads to:** [[batch-vs-streaming]]
- **Asked together with:** [[kafka-messaging]]
