---
id: gcp-bigquery
title: GCP and BigQuery
tier: 2
priority: should-know
sources: [obenner/bigquery, obenner/gcp, cookbook]
---

# GCP and BigQuery

## Say it in one line
BigQuery is a serverless columnar warehouse in which storage and compute are fully separate, so you never size a cluster — you only control how many bytes a query touches and how many slots it may use.

## Must be able to recite
- **Serverless** — There is no cluster to provision, patch or resize; you submit SQL and Google allocates compute for the life of the query.
- **Dremel, Capacitor, Colossus, Jupiter** — Dremel is the execution engine (a tree of leaf workers and mixers), Capacitor the columnar storage format, Colossus the distributed filesystem, Jupiter the network fast enough to shuffle between them.
- **Slot** — One unit of BigQuery compute; a query is split into stages and stages queue when slots run out, which is why a big query gets slower rather than failing.
- **On-demand vs capacity pricing** — On-demand bills per terabyte scanned with the first TiB each month free; capacity pricing (Editions: Standard, Enterprise, Enterprise Plus) bills autoscaling slot-hours with optional commitments (the source's "flat-rate" naming was retired in 2023).
- **Storage pricing** — Active storage drops to roughly half price as long-term storage once a table partition has not been modified for 90 days, and you can choose physical-byte billing when the data compresses well.
- **Partitioning** — Split a table by ingestion time, a DATE/TIMESTAMP column or an integer range, up to 4,000 partitions; a filter on the partition column prunes whole partitions and directly cuts the bytes billed.
- **Clustering** — Sorts data inside each partition by up to four columns so BigQuery can skip blocks; it suits high-cardinality filters and join keys where partitioning would create too many partitions.
- **Choosing between them** — Partition on the coarse date you always filter on, cluster on the selective ids you filter or join on; clustering costs nothing extra and BigQuery re-clusters in the background.
- **`require_partition_filter`** — A table option that rejects any query without a partition predicate, and the single most effective cost guard you can set.
- **Storage Write API vs legacy streaming inserts** — The Write API is the current path with exactly-once semantics and lower cost; legacy `insertAll` lands rows in a streaming buffer where they cannot be updated or deleted for a while.
- **View vs materialized view** — A view is stored SQL re-run every time; a materialized view stores results, refreshes incrementally, and BigQuery will silently rewrite a query on the base table to use it.
- **Nested and repeated fields** — STRUCT and ARRAY let you keep a one-to-many relationship in one table and `UNNEST` it at query time, which removes a join and therefore a shuffle.
- **Time travel and snapshots** — `FOR SYSTEM_TIME AS OF` reads a table as it was up to seven days ago (configurable down to two), and a table snapshot is a cheap zero-copy point-in-time clone for longer retention.
- **Query cache and reservations** — Identical queries on unchanged tables are served free from a 24-hour cache, and slot reservations assigned to projects stop one team's backfill from starving the BI dashboards.
- **The rest of the GCP data stack** — GCS is the lake, Pub/Sub the message log, Dataflow (Apache Beam) the unified batch and streaming engine, Dataproc managed Spark/Hadoop, Composer managed Airflow, Datastream serverless database CDC into BigQuery.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ What is BigQuery and how does it handle storage and processing? — A fully managed serverless columnar warehouse that stores data in Capacitor on Colossus and executes queries with Dremel, keeping storage and compute independent so each scales and is billed separately.
- ★ Explain partitioning in BigQuery. — The table is divided into segments by ingestion time, a date/timestamp column or an integer range; queries that filter on that column read only the matching partitions, which cuts both time and cost.
- ★ What is clustering and how does it optimise query performance? — Rows are physically sorted inside each partition by up to four columns, so the engine can skip blocks that cannot match the filter; it is the tool for selective, high-cardinality predicates and join keys.
- ★ How do you decide between partitioning and clustering? — Partition on the one coarse time column that nearly every query filters on, then cluster on the columns used for selective filters and joins; partitioning by anything high-cardinality just produces thousands of tiny partitions.
- ★ Explain slots, and the difference between slots and slot reservations. — A slot is a unit of query compute; a reservation is a named pool of purchased slots you assign to projects or folders so their workloads get predictable capacity and cannot starve each other.
- ★ What pricing models does BigQuery offer, and how do you control cost? — On-demand per terabyte scanned or capacity-based slot pricing; you control it by partitioning and clustering, selecting only the columns you need, requiring partition filters, using the cache and materialized views, and setting per-query and per-user byte limits.
- ★ What are the best practices for optimising query performance in BigQuery? — Filter on partition and cluster columns, avoid `SELECT *`, denormalise with nested fields instead of large joins, put the biggest table first in a join, aggregate before joining, and reuse materialized views.
- ★ What is the difference between a view and a materialized view? — A view is a saved query executed against the base tables each time, so it costs a full scan; a materialized view physically stores the pre-computed result, refreshes incrementally, and can be substituted into queries automatically.
- ★ Explain streaming inserts and the streaming buffer. — Rows pushed through the streaming API are immediately queryable but sit in a buffer before being written into columnar storage, during which they cannot be updated or deleted; the current recommendation is the Storage Write API rather than legacy `insertAll`.
- ★ What are the limitations of BigQuery streaming inserts? — Higher cost than batch loads, per-table and per-project rate quotas, no update or delete of buffered rows, and duplicate rows unless you supply insert ids or use the Write API's exactly-once mode.
- ★ Explain nested and repeated fields, and why they matter. — A STRUCT nests related columns and an ARRAY repeats values inside one row, so a one-to-many relationship stays in a single table; querying with `UNNEST` avoids a join and therefore avoids shuffling data across slots.
- ★ How do you load data into BigQuery, and what are the ingestion options? — Batch loads from GCS or local files through the console, `bq` CLI or API (free), streaming through the Storage Write API, scheduled pulls through the Data Transfer Service, and pipelines built in Dataflow.
- ★ Explain federated queries and external tables. — BigQuery reads data in place from GCS, Cloud SQL, Bigtable or Google Sheets without loading it, which is useful for occasional joins to reference data but slower and less predictable than native storage.
- ★ How does BigQuery handle schema changes and schema evolution on large tables? — Adding a nullable column or relaxing a mode is a metadata-only operation; anything else (changing a type, dropping a column, repartitioning) means rewriting the table, so you create a new table and swap.
- ★ What is time travel in BigQuery? — You can query, restore or copy a table as it was at any point in the retention window (up to seven days by default), which is how you recover from an accidental delete or a bad load.
- ★ Explain the query cache. — Results of a query are cached for 24 hours and an identical query on unchanged tables is served from cache with no charge; non-deterministic functions, wildcard tables and writing to a destination table defeat it.
- What is the difference between BigQuery and a traditional relational database? — BigQuery is a columnar, distributed, serverless analytical store optimised for large scans with no indexes and no per-row transactions; a relational OLTP database is row-based, indexed and optimised for many small reads and writes.
- ★ How do you control access and permissions in BigQuery? — IAM roles at organisation, project, dataset, table and column level, authorised views and row-level access policies for restricted slices, and service accounts for pipelines.
- ★ What is Cloud Dataflow and when do you use it? — Managed Apache Beam, where the same pipeline code runs in batch or streaming with autoscaling and no cluster; it is the GCP answer for transformation, windowing and enrichment between Pub/Sub and BigQuery.
- What is Cloud Dataproc and how does it differ from Dataflow? — Dataproc is managed Spark and Hadoop, so you lift existing Spark/Hive jobs and control the cluster; Dataflow is serverless Beam with no cluster and is the better fit for new streaming pipelines.
- ★ What is Cloud Pub/Sub? — A managed, globally available publish/subscribe message service with at-least-once delivery, subscriptions per consumer and no partition management, which is GCP's ingestion buffer for event-driven pipelines.
- ★ What is Cloud Composer? — Managed Apache Airflow, used to schedule and monitor multi-step BigQuery, Dataflow and Dataproc workloads with dependencies, retries and backfills.
- ★ How does GCP store data — what are the main options? — GCS for objects, BigQuery for analytics, Cloud SQL for managed relational, Spanner for globally distributed relational, Bigtable for wide-column NoSQL at low latency, Firestore for documents, Memorystore for Redis caching.
- ★ How do you monitor and troubleshoot BigQuery query performance? — Read the query plan and execution statistics per stage, query `INFORMATION_SCHEMA.JOBS` for bytes scanned, slot-milliseconds and duration, and watch for skewed stages and repartitioning.
- What is the purpose of `INFORMATION_SCHEMA`? — Metadata views over datasets, tables, columns, partitions and jobs, which is where you find unused tables, partition sizes and the most expensive queries.
- ★ How do you optimise storage cost in BigQuery? — Partition-level expiry, drop or archive unused tables, let cold partitions fall into long-term storage, avoid duplicating the same data in derived tables, and consider physical-byte billing.
- What is BI Engine? — An in-memory acceleration layer in front of BigQuery that makes dashboards interactive by caching hot columns, which matters when a Looker or Data Studio page fires many small queries.
- What are wildcard tables and date-sharded tables? — Wildcard syntax queries many tables matching a prefix, which is how you read legacy `events_YYYYMMDD` shards; the modern equivalent is a single partitioned table, which is cheaper and cacheable.
- What is BigQuery ML? — Training and scoring models with `CREATE MODEL` in SQL inside BigQuery, so analysts can build regressions, classifiers and forecasts without moving data (`TRANSFORM` handles feature engineering, `EVALUATE` reports metrics).
- What is the BigQuery Storage API? — A high-throughput API for reading BigQuery data directly into Spark, Beam or pandas without exporting to GCS first, and for writing with the Storage Write API.
- What is BigQuery Omni? — Running BigQuery's engine against data that stays in AWS S3 or Azure storage, queried from one BigQuery interface for multi-cloud estates.
- How does BigQuery handle data deduplication? — It does not do it for you: deduplicate before load, or use `MERGE` or a `ROW_NUMBER()` window on the natural key in the transformation step.
- How do you automate BigQuery jobs? — Scheduled queries for simple recurring SQL, Cloud Composer for real DAGs with dependencies, and Cloud Functions or Workflows triggered by events such as a file landing in GCS.
- What is Datastream? — Serverless change data capture from Oracle, MySQL, PostgreSQL and SQL Server into BigQuery or GCS, which is how operational data reaches BigQuery continuously without a hand-built CDC pipeline (not in sources, but standard).
- How does BigQuery handle consistency? — Queries see a consistent snapshot of each table and single-statement DML is atomic (the source claims eventual consistency; that is wrong — the caveat is only that streamed rows may still be in the buffer).

## Traps
- Saying BigQuery is fast "because it is in-memory": it is columnar scanning plus massive parallelism plus a very fast network — name Dremel and slots instead.
- Stating that partitioning and clustering both reduce bytes scanned and stopping there: the interviewer wants the selection rule, which is coarse time column to partition, selective id columns to cluster.
- Believing `LIMIT` reduces cost: on-demand billing counts the bytes the scan reads, so `SELECT * ... LIMIT 10` on a 5 TB table still bills for the columns scanned; only pruning, column selection and the cache reduce it.
- Repeating that BigQuery cannot UPDATE or DELETE: DML has worked for years, and the real constraints are quotas, buffered streaming rows and the cost of rewriting large partitions.
- Streaming every row when a five-minute batch load would do: batch loads are free and streaming is not, so streaming needs a latency requirement to justify it.
- Creating date-sharded tables because an old tutorial did: one partitioned table is cheaper, cacheable and does not blow up the metadata.

## Graph
- **Needs first:** [[cloud-fundamentals]]
- **Leads to:** [[warehouse-engines]]
- **Asked together with:** [[partitioning-layout]]
