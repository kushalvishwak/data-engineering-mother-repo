---
id: hive-impala
title: Hive and Impala
tier: 1
priority: should-know
sources: [obenner/hive, obenner/impala, obenner/hadoop, cookbook]
---

# Hive and Impala

## Say it in one line
Hive is a SQL layer that stores only metadata and compiles HiveQL into distributed batch jobs over files in HDFS or object storage; Impala is an always-on MPP engine that queries the same tables and the same metastore interactively without MapReduce.

## Must be able to recite
- **Hive** — SQL over files with schema-on-read, so loading is just a file move and a bad record surfaces at query time rather than at load time.
- **Metastore** — a relational database (usually MySQL or Postgres) plus a Thrift service holding databases, tables, columns, partitions, SerDes and file locations; Spark, Impala, Presto and Trino all read this same catalogue.
- **Managed vs external table** — Hive owns data and metadata for a managed table so `DROP` deletes the files, whereas an external table is metadata only and `DROP` leaves the data untouched.
- **Partitioning** — stores rows in directories named by column value so the planner prunes whole directories; only for low-cardinality columns like date or region.
- **Bucketing (`CLUSTERED BY`)** — hashes a high-cardinality column into a fixed number of files inside each partition, which enables sampling and bucketed map-side joins without creating millions of directories.
- **Partition vs bucket** — partitions are directories with an unbounded count pruned by value, buckets are a fixed file count addressed by hash.
- **Dynamic partitioning** — the `INSERT` derives partition values from the data; it needs `hive.exec.dynamic.partition=true` and non-strict mode when no static partition is supplied.
- **Strict mode** — `hive.mapred.mode=strict` rejects a query that scans a partitioned table without a partition filter, plus unbounded `ORDER BY` and cartesian joins.
- **SerDe** — the serialiser/deserialiser that maps raw bytes to typed columns (LazySimpleSerDe for delimited text, OpenCSVSerDe, RegexSerDe, JsonSerDe), and a custom SerDe is how you read a bespoke format.
- **ORC vs Parquet** — both are columnar with per-stripe or row-group statistics for predicate pushdown; ORC is native to Hive with ACID and bloom filter support, Parquet is the ecosystem default used by Spark, Impala and Athena.
- **Vectorisation** — `hive.vectorized.execution.enabled` processes batches of 1024 rows per operator call instead of one row at a time, and requires a columnar format.
- **Execution engines** — Tez runs the query as one DAG with no per-stage HDFS write, LLAP adds long-lived daemons with caching for interactive latency, and Hive-on-Spark is `hive.execution.engine=spark` (the sources say Hive compiles to MapReduce; that has been the deprecated fallback since Hive 2).
- **`ORDER BY` vs `SORT BY` vs `DISTRIBUTE BY` vs `CLUSTER BY`** — `ORDER BY` forces one reducer for a global sort, `SORT BY` sorts within each reducer, `DISTRIBUTE BY` routes equal keys to the same reducer, and `CLUSTER BY` is both on one column.
- **Impala architecture** — an `impalad` on every DataNode acts as coordinator and executor, `statestored` tracks liveness, `catalogd` broadcasts metadata changes; no MapReduce, LLVM-generated code per query and results streamed as they are ready.
- **`REFRESH` vs `INVALIDATE METADATA`** — `REFRESH table` reloads the file and block list for one table after new data lands, while `INVALIDATE METADATA` throws away the cached catalogue entry so Hive-side DDL is picked up, and the un-scoped form is expensive.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ What is the Hive metastore and why does it matter? — A relational catalogue of table, column, partition, format and location metadata; lose it and the files in HDFS are just bytes, which is why it is backed up and shared across engines.
- ★ Managed vs external tables — which do you use? — Managed when Hive owns the lifecycle and a `DROP` should delete data; external for raw landing zones and data shared with other tools, because dropping it must not destroy the files.
- ★ Partitioning vs bucketing. — Partitioning creates one directory per value and prunes at plan time; bucketing hashes into a fixed number of files for join and sampling efficiency, and is what you use when the column has too many distinct values to partition on.
- ★ How do you pick a partition column? — Low cardinality and actually used in `WHERE` filters, usually a date; the sources' warning is explicit — do not over-partition, because tiny partitions become NameNode and metastore overhead.
- ★ What is a SerDe, and when do you write a custom one? — It converts file bytes to columns and back; write your own for a format no built-in SerDe handles, such as a fixed-width or proprietary log layout.
- ★ Why is Hive not suitable for OLTP? — Every statement is a distributed batch job with seconds of start-up latency, and there is no indexed single-row access path; the sources' stronger claim that Hive cannot update or delete at all is outdated, since Hive 0.14 added ACID tables on ORC and Hive 3 makes managed tables transactional by default.
- ★ What does schema-on-read mean? — The schema is applied when the data is read rather than enforced on write, so loading is cheap but type and delimiter mismatches surface as `NULL`s at query time.
- ★ `ORDER BY` vs `SORT BY` in Hive. — `ORDER BY` guarantees a total order by funnelling everything through a single reducer, which does not scale; `SORT BY` only guarantees order within each reducer.
- ★ What is the use of ORC, and how does it compare to Parquet? — ORC gives columnar storage, lightweight indexes and per-stripe statistics with one output file per task; Parquet is equivalent for reads and is the more portable choice outside Hive.
- ★ How do you improve the performance of a Hive query? — Partition prune, store in ORC or Parquet with statistics, enable vectorisation and cost-based optimisation, use a map-join for small sides, and run on Tez or LLAP rather than MapReduce.
- ★ How do you fix an out-of-memory error on a Hive join? — Broadcast the small table with a map-join, and make sure the largest table is the streamed one — rightmost in the `JOIN`, or named in a `/*+ STREAMTABLE(t) */` hint, because Hive buffers every table except the streamed one.
- ★ In a join query, what order should the tables be in? — Smallest first, largest last, since the last table is streamed and the others are held in memory.
- ★ What is bucketing used for besides even file sizes? — Sampling (`TABLESAMPLE`), and bucketed map-side joins when both tables are bucketed and sorted on the same key with compatible bucket counts.
- ★ What are the components of Hive? — A UI or JDBC client, the driver managing the session, the compiler producing a plan, the metastore supplying metadata, and the execution engine running the DAG.
- ★ Difference between Hive and HBase. — Hive is a batch SQL warehouse layer over files; HBase is a NoSQL key-value store on HDFS with row-level random reads, writes and updates but no SQL of its own.
- ★ What is a skewed table in Hive? — A table declared `SKEWED BY` on values that appear disproportionately often, so those values are stored in separate files and can be handled separately at query time.
- ★ What is the difference between Hive and Impala, and when do you use each? — Impala runs its own always-on C++ daemons with LLVM codegen and no MapReduce, giving second-scale interactive and BI queries; Hive or Spark for long-running batch ETL, very large joins that must spill, and custom SerDes or UDTFs.
- ★ How does Impala get its speed? — No MapReduce start-up, no materialising of intermediate results to disk, runtime code generation with LLVM, SIMD instructions, and locality-aware I/O scheduling.
- ★ Does Impala need Hive or MapReduce? — It needs the Hive metastore, not Hive itself and not MapReduce at all; Hive is still handy for writing formats Impala cannot insert into.
- ★ Why must you run `REFRESH` or `INVALIDATE METADATA`? — Impala caches metadata aggressively, so data loaded through Hive or Spark needs `REFRESH` and DDL done outside Impala needs `INVALIDATE METADATA`.
- ★ How does Impala perform joins? — Cost-based choice between a broadcast join, which ships the small side to every node, and a partitioned join, which hash-shuffles both sides; the plan depends on `COMPUTE STATS` having been run.
- ★ What happens in Impala when a query exceeds available memory? — Older versions cancelled the query outright; from Impala 2.0 joins and aggregations spill to a disk work area, and `MEM_LIMIT` caps a query.
- ★ Is there a single point of failure in Impala? — Any `impalad` can coordinate a query, so there is no SPOF for query submission, but a query dies if a node running one of its fragments fails, and the metastore and NameNode are still shared dependencies.
- ★ What can Impala not do that Hive can? — No custom SerDe framework, no `UPDATE` or `DELETE` on HDFS tables, no streaming input, no indexes, and no checkpointing within a query.
- Where does Hive store table data by default? — Under the warehouse directory, `/user/hive/warehouse/<db>.db/<table>` in HDFS, unless the table specifies a `LOCATION`.
- What is `hive.exec.mode.local.auto` / how can Hive avoid launching a distributed job? — Small inputs can run locally, and simple `SELECT`/filter/`LIMIT` queries can be turned into a single fetch task with `hive.fetch.task.conversion`.
- What is the point of `DISTRIBUTE BY`? — It controls which reducer a row lands on, which is how you guarantee all rows for a key are processed and written together.
- What is `STREAMTABLE`? — A join hint naming the table to stream instead of buffer; without it Hive streams the rightmost table.
- What are Hive's complex types? — `ARRAY`, `MAP`, `STRUCT` and the incomplete `UNIONTYPE`, with `EXPLODE()` and other table-generating functions to flatten them into rows.
- What is a UDF, UDAF and UDTF in Hive? — Scalar function, aggregate function and table-generating function; Impala supports UDFs and UDAFs (C++ or reused Java UDFs) but not UDTFs.
- What are the pros and cons of archiving a partition? — Fewer files for the NameNode to track and the partition is still queryable, but queries get slower and you save no space.
- Can a view have the same name as a table, and can you load into a view? — No to both; view names share the namespace with tables, and a view is never the target of `INSERT` or `LOAD`.
- What is HCatalog? — A table and storage abstraction over the metastore so Pig, MapReduce and other tools see the same relational view of Hive tables.
- Does Hive support indexes? — Hive's index feature existed but was removed in Hive 3; use partitioning, bucketing and ORC/Parquet min-max plus bloom filters instead. *(not in sources, but standard)*

## Traps
- Saying flatly "Hive cannot do updates or deletes" — that was true pre-0.14 and is what the sources say; ACID ORC tables support `MERGE`, `UPDATE` and `DELETE`, so the correct answer is that it works but is batch-speed and still wrong for OLTP.
- Partitioning on a high-cardinality column such as `user_id` or a timestamp — you get millions of directories and tiny files, which is exactly the problem bucketing solves.
- Saying "Hive converts queries into MapReduce" in the present tense — Tez is the default from Hive 2, with LLAP for interactive and Spark as an option; MapReduce is deprecated.
- Mixing up the drop semantics — dropping an external table and expecting the files to be gone, or dropping a managed table and expecting them to survive.
- Repeating the source's fix for a join OOM ("change `RIGHT OUTER JOIN` to `LEFT OUTER JOIN`") — the real levers are map-join for the small side and stream the largest table last.
- Pitching Impala as a drop-in Hive replacement — it shares the metastore but has no SerDe framework, no UDTFs, no row-level writes, and needs `REFRESH`/`INVALIDATE METADATA` when other engines change the data.

## Graph
- **Needs first:** [[hadoop-hdfs]], [[sql-semantics]]
- **Leads to:** [[warehouse-engines]]
- **Asked together with:** [[file-formats]], [[partitioning-layout]]
