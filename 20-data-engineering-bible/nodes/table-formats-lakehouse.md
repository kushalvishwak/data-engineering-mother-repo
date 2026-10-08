---
id: table-formats-lakehouse
title: Table Formats and the Lakehouse — Iceberg, Delta, Hudi
tier: 1
priority: must-know
sources: [obenner/iceberg, obenner/hudi, obenner/cost-optimization, obenner/data-governance, obenner/cdc, obenner/dbt, devinterview, cookbook]
---

# Table Formats and the Lakehouse — Iceberg, Delta, Hudi

## Say it in one line
A table format is a metadata layer over Parquet files on object storage that turns "files in folders" into a real table with atomic commits, snapshots, time travel and row-level updates.

## Must be able to recite
- **Table format** — metadata that describes which files belong to a table at each version; the data files stay ordinary Parquet or ORC, what you gain is transactions and evolvable structure.
- **Why bare files fail** — a directory listing has no transaction boundary, so readers can see half-written output, `INSERT OVERWRITE` is not atomic, and deleting one row means rewriting a partition by hand.
- **Atomic commit** — the writer stages new data files and then swaps a single metadata pointer, so a reader sees either the old snapshot or the new one and never a mixture.
- **Snapshot** — a point-in-time list of the data and delete files that make up the table; every commit creates a new one, which is what allows consistent reads while writers keep working.
- **Time travel** — querying the table as of an earlier snapshot or timestamp, for debugging regressions, auditing, reproducing an old report, or computing a backfill against a frozen view.
- **Optimistic concurrency** — each writer builds metadata from the snapshot it read and then attempts to commit; if the base snapshot has moved the commit is rejected and retried, so no update is silently lost.
- **Schema evolution by field ID** — Iceberg tracks columns by unique numeric IDs rather than by name or position, so add, drop, rename and reorder do not misread old files.
- **Hidden partitioning** — the partition transform (`day(ts)`) lives in table metadata, not in directory names, so queries filter on `ts` and still prune, and the physical layout stops leaking into query logic.
- **Partition evolution** — the partition spec can change (day to month, or a new field) without rewriting history; old files keep their old spec and both are pruned correctly.
- **Copy-on-write (COW)** — an update rewrites the whole affected data file: write amplification, but clean fast reads. Default choice when reads dominate.
- **Merge-on-read (MOR)** — an update writes a small delta or delete file and readers merge at query time: fast writes, heavier reads, and it degrades without compaction.
- **Delete files** — Iceberg records deletes as *positional* (row positions inside a named file) or *equality* (rows matching a key predicate), avoiding full rewrites but slowing reads until compacted.
- **Maintenance** — compact data files to a target size, rewrite manifests, expire old snapshots, remove orphan files; skipping this is the usual reason a lakehouse becomes slow and expensive.
- **Catalog** — the component mapping a table name to its current metadata pointer (Hive Metastore, REST catalog, AWS Glue, Unity Catalog); it determines authorisation and which engines can share the table.
- **Lakehouse vs warehouse** — a lakehouse keeps open-format files on cheap object storage and gets ACID from the table format, so any engine can read it; a warehouse owns a proprietary storage format and trades lock-in for tighter performance, concurrency and governance.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ What problem do Iceberg, Delta and Hudi solve over plain Parquet datasets? — Bare file datasets have no transactional guarantees and no consistent metadata; table formats add atomic commits, consistent snapshots, reliable schema and partition evolution, row-level updates and deletes, and metadata-driven pruning.
- ★ What is copy-on-write versus merge-on-read, and how do you choose? — COW rewrites the columnar file on update (write amplification, simple fast reads); MOR writes base files plus delta logs merged at read time (fast writes, complex reads). Choose COW when read latency matters and updates are moderate, MOR for near-real-time ingest if you can operate compaction.
- ★ Why does the small-files problem happen and how do you mitigate it? — Frequent commits, streaming checkpoints and over-granular partitions produce tiny files, and planning plus metadata overhead then dominates the scan; you set target file sizes, batch writes, and run compaction or clustering.
- ★ What is time travel and why is it useful? — Querying the table "as of" a previous snapshot or timestamp, for debugging regressions, auditing changes, reproducing past reports, and safe backfills computed against a stable snapshot.
- ★ What is hidden partitioning? — Partitioning is defined in table metadata as a transform rather than as user-managed folder paths, so engines still prune but you are not tied to a physical directory layout, which also makes partition evolution safe.
- ★ What is partition evolution and why does it matter? — Changing the partition spec over time without rewriting historical data, because query patterns and volumes change and the right partitioning today is often wrong in a year.
- ★ Iceberg vs Delta vs Hudi — when would you choose each? — Iceberg for open, engine-agnostic tables with strong metadata and evolution (Spark plus Trino plus Flink); Hudi for CDC-heavy upsert and delete workloads with near-real-time ingest; Delta when you are aligned with the Delta/Databricks ecosystem. The real drivers are your engines, governance and update requirements.
- ★ What is an Iceberg catalog and what options exist? — The store holding namespace information and the pointer to each table's current metadata: Hive Metastore, the REST catalog, or a cloud catalog such as AWS Glue; the choice affects authorisation, interoperability and operational complexity.
- ★ What are a record key, partition path and precombine field in Hudi? — The record key uniquely identifies a row like a primary key, the partition path controls grouping and pruning, and the precombine field (for example `updated_at`) resolves duplicate records for the same key so upserts are deterministic.
- ★ How do you handle CDC on a lakehouse table? — Ingest change events into an append-only raw log, standardise ordering and deduplicate on record key plus a sequence or precombine field, then apply deterministic upserts and deletes to build the current-state table, and monitor lag and compaction.
- ★ What is a data lake, what is a warehouse, and is there such a thing in between? — A lake stores raw multi-format files cheaply with schema on read; a warehouse stores modelled, governed, query-optimised tables; a lakehouse is open files on object storage plus a table format that supplies ACID, time travel and evolution.
- What is a snapshot in Iceberg? — A point-in-time view of the table that references a set of data and delete files through a manifest list and manifests, so readers get consistent results even while writers append or modify.
- How does Iceberg handle concurrent writes? — Optimistic concurrency control: a writer creates new metadata from a known current snapshot and attempts to commit, and if the base snapshot changed the commit conflicts and must be retried, which prevents silent lost updates.
- How does schema evolution work in Iceberg? — Columns are tracked by unique field IDs, so add, drop and rename are safe and historical snapshots stay queryable; some type changes still depend on engine support, so consumers should not assume a fixed schema.
- What are equality deletes and positional deletes? — Equality deletes remove rows matching a key predicate such as `id = 123`; positional deletes remove specific row positions inside named data files. Both avoid rewriting whole files, but a build-up of delete files hurts reads until compaction.
- How do upserts and merges work on these tables? — The engine implements `MERGE INTO` (Spark, Flink, Trino), producing new data files and delete files depending on the write mode; you then compact and expire snapshots as routine maintenance.
- What maintenance operations do Iceberg tables need? — Rewrite data files to a target size, rewrite manifests to shrink metadata, expire old snapshots, and delete orphan files; these keep query planning and storage cost bounded.
- How would you migrate an existing Parquet dataset to Iceberg? — Create the Iceberg table schema and either register the existing files in place where the layout conforms, or rewrite the data through Spark/Flink for safety; then validate row counts and key constraints, compare query performance, and switch readers over.
- What is Apache Hudi? — A lakehouse framework that brings upserts, deletes and incremental reads to object storage by managing a timeline and table metadata that batch and streaming engines share.
- What is compaction in Hudi, and what is clustering? — Compaction merges MOR delta log files into base columnar files to restore read performance; clustering reorganises files for size, sort order and locality to fix small files and improve pruning.
- How do you enforce data retention, and how do you satisfy GDPR erasure on a lakehouse? — Partition expiry jobs, object-storage lifecycle rules and snapshot expiration for retention; for erasure, targeted row-level deletes where supported, or reprocessing from raw without the subject, ideally with personal data isolated so deletion does not rewrite everything.
- What operational metrics would you monitor on these tables? — Commit and compaction backlog, file count and average file size per partition, write latency, failed commits, and scan metrics; alerts usually fire on rising small-file counts and compaction lag.
- How does Delta Lake's transaction log differ from Iceberg's metadata? — Delta keeps an ordered JSON/Parquet commit log (`_delta_log`) that readers replay to reconstruct table state, while Iceberg keeps a tree of metadata file, manifest list and manifests that readers traverse; the guarantees are equivalent, the planning characteristics differ. (not in sources, but standard)

## Traps
- Calling Iceberg or Delta a *file* format. They are table formats — the data is still Parquet or ORC, only the metadata layer is new.
- Saying "it gives you ACID" and stopping. Name the mechanism: an atomic swap of one metadata pointer, plus optimistic concurrency against the snapshot you read.
- Treating merge-on-read as free write throughput. Without scheduled compaction, delete-file counts and read latency climb until queries fail their SLA.
- Assuming hidden partitioning means no partitioning decisions. You still choose the transform and its granularity; you have only stopped encoding it in directory names.
- Claiming the lakehouse replaces the warehouse outright. Banks and large enterprises still serve marts from a warehouse engine for concurrency, governance and BI latency, with the lakehouse holding raw and curated layers.
- Leaving maintenance out of a design answer. Compaction, snapshot expiry and orphan-file cleanup are part of the design and of the cost model, not an afterthought.

## Graph
- **Needs first:** [[file-formats]], [[warehouse-architecture]]
- **Leads to:** [[warehouse-engines]]
- **Asked together with:** [[cdc-ingestion]]
