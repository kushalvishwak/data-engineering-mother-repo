---
id: partitioning-layout
title: Partitioning, Clustering and Physical Layout
tier: 1
priority: must-know
sources: [obenner/hive, obenner/hadoop, obenner/impala, obenner/bigquery, obenner/redshift, obenner/greenplum, obenner/cost-optimization, obenner/iceberg, obenner/hudi, devinterview, cookbook]
---

# Partitioning, Clustering and Physical Layout

## Say it in one line
Physical layout decides how much data a query is allowed to skip: partitions prune whole directories or file groups, and clustering, bucketing and sort order prune files and row groups inside them.

## Must be able to recite
- **Partitioning** — splitting a table into physically separate groups of files by column value, so a filter on that column reads only the matching groups.
- **Partition pruning** — the planner eliminates partitions that cannot satisfy the predicate before reading anything; a filter on a non-partition column gives you no pruning at all.
- **Good partition column** — low to moderate cardinality, present in nearly every query's `WHERE` clause, and usually time-based (`event_date`); date plus at most one more dimension covers most tables.
- **Over-partitioning** — thousands of tiny partitions cost more in metadata, listing and task startup than they save in pruning; Hive's own guidance is not to partition into partitions that are too small because it is overhead on the NameNode.
- **Small-files problem** — many tiny files make the engine spend more time opening and planning files than reading data, inflate metastore and NameNode memory, multiply object-storage list calls, and weaken compression and statistics.
- **Target file size** — roughly 128 MB to 1 GB per file (Impala's default Parquet file size is 256 MB); too small and file count dominates, too large and you lose parallelism on selective queries.
- **Bucketing / `CLUSTERED BY`** — hash a column into a fixed number of buckets so the file count stays bounded no matter how the data grows; it also enables map-side bucket-to-bucket joins.
- **Partition versus bucket** — partition on what you filter, bucket on what you join or look up by; partitions are directories whose count grows with the data, buckets are a fixed number of files.
- **Clustering and Z-ordering** — sorting or interleaving rows within a partition so min/max statistics become tight and predicate pushdown can skip files; a plain sort favours the leading column, Z-order serves several filter columns at once.
- **Sort key** — the warehouse equivalent of clustering: physical on-disk order (Redshift sort key, BigQuery clustering) that lets zone maps skip blocks.
- **Distribution key** — in an MPP warehouse it decides *which node or slice* holds a row; matching it to the join key avoids redistributing data at query time.
- **Data skew** — one partition or key holds far more rows than the rest, producing straggler tasks; detect it from task-duration and partition-size distributions, fix it by salting, repartitioning, broadcasting the small side, or a skew-aware join.
- **Never partition on high cardinality** — no partitioning on IDs, second-precision timestamps or free text; derive a date or hash into buckets instead.
- **Static versus dynamic partition writes** — dynamic writes (one job touching many partitions) are the usual source of a small-file explosion; control it with a repartition before write or the engine's target-file-size setting.
- **Layout evolution** — Hive-style directory partitioning is baked into paths so changing it means a full rewrite, whereas Iceberg's hidden partitioning lets you evolve the spec without rewriting history.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ How does partitioning affect cost and performance? — Good partitioning reduces bytes scanned through pruning; bad partitioning creates too many small partitions and files, adding metadata and planning overhead, and it should be re-evaluated as workloads evolve.
- ★ How do you choose a partition column? — Pick what almost every query filters on, normally a date, at a granularity where each partition holds a few hundred megabytes; avoid IDs and high-precision timestamps, and reconsider it when volume changes.
- ★ What is the small-files problem and why does it increase cost? — Engines spend more time opening and planning files than processing data and scan efficiency falls; small files come from streaming writes and over-granular partitions, and the fix is compaction or clustering.
- ★ How do you choose a target file size for Parquet tables? — Balance parallelism against overhead: too small inflates file count and planning cost, too large reduces parallelism and slows selective queries; many teams target hundreds of megabytes, tuned per engine and query pattern.
- ★ What is bucketing in Hive and how is it different from partitioning? — Bucketing hashes a column into a user-defined number of buckets, so a high-cardinality column such as `user_id` yields a manageable file count instead of millions of partitions, and it enables map-side joins.
- ★ What is clustering and how does it optimise query performance? — It physically groups related rows within a partition by one or more column values so the engine can skip irrelevant data during a scan.
- ★ What is partition pruning (data pruning)? — Eliminating irrelevant partitions during query execution based on the query predicates, which is exactly why a filter on a non-partition column buys you nothing.
- ★ What is a sort key in Redshift, and what is a distribution key? — The sort key sets the on-disk order within each node so scans skip blocks; the distribution key decides which slice a row lands on, and matching it to the join key minimises data movement.
- ★ What is data skew and what does it do to a query? — An uneven distribution of data across partitions or segments, so a few tasks or nodes do most of the work and become stragglers, producing uneven runtimes and hot nodes.
- ★ How do you detect and fix skew? — Inspect task duration distributions and partition size metrics, then salt the key, repartition, broadcast the small side, or switch the join strategy; MPP engines also offer redistribution.
- Can you change the sort key or distribution key of an existing table? — The source says no, you must create a new table and copy; that is outdated — Redshift has supported `ALTER TABLE ALTER SORTKEY` and `ALTER DISTKEY` since 2019 (and automatic table optimisation), though it still rewrites data in the background.
- What partitioning strategies exist in a warehouse? — Range (normally date), list and hash; time-based range partitioning plus clustering on the next-most-filtered column covers most analytics tables.
- What are the important steps when partitioning a table? — Do not over-partition into tiny partitions, enable dynamic partitioning deliberately (`hive.exec.dynamic.partition`, non-strict mode) and keep one static partition, load into a staging table first, then insert into the partitioned table.
- What are the benefits of partitioned tables in BigQuery? — Faster queries and lower cost because less data is scanned, the ability to target a single partition, and simpler lifecycle management through partition expiry and archiving.
- What is the difference between partitioning and sharding? — Partitioning splits one table into parts inside one system so the planner can prune; sharding splits a dataset across independent nodes by a shard key so the system can scale out.
- What is a skewed table in Hive? — A table declared `SKEWED BY` on values that occur disproportionately often, so those values are written to separate files and handled separately, which improves query performance.
- What does `CLUSTERED BY` do in Hive? — It distributes rows across reducers by hash and then sorts within each bucket; it is declared at table creation but the benefit appears at query time.
- What are the pros and cons of archiving a Hive partition? — It reduces the number of files the NameNode tracks and the archive is still queryable, but queries become slower and less efficient and you save no storage.
- How do you stop a partition being dropped or queried in Hive? — `ALTER TABLE ... ENABLE NO_DROP` prevents dropping and `ENABLE OFFLINE` prevents querying while leaving the metadata readable.
- Does reducing the HDFS or Parquet block size make queries faster? — No: smaller blocks mean more splits, more tasks and more overhead, and query engines do not rewrite your data; size blocks and files to the workload instead.
- How does layout interact with shuffle in Spark? — Shuffle redistributes data across executors for joins, group-by and distinct; data already partitioned or bucketed on the join key lets the engine shrink or skip the shuffle entirely.
- How do you load a large CSV into a partitioned table? — Land it in an unpartitioned external or text table first, then `INSERT ... SELECT` into the partitioned table with the partition key columns last, so the engine writes each partition correctly.
- What is Z-ordering and when would you use it? — A space-filling-curve interleave of several columns so files carry tight min/max ranges on all of them at once; use it when queries filter on two or three columns and no single sort order serves them all. (not in sources, but standard)
- How many partitions is too many? — Treat a few hundred megabytes per partition as the floor, and treat a table whose partition list a metastore or planner cannot enumerate quickly as already misdesigned. (not in sources, but standard)

## Traps
- Partitioning on a high-cardinality column because "more pruning must be better". You get one tiny file per partition, and the planning overhead exceeds the scan you saved.
- Assuming a partitioned table is automatically fast. Pruning only happens when the query filters on the partition column directly — wrapping it in a function or comparing it to a non-literal can disable pruning.
- Confusing partitioning with distribution. Partitioning controls what is *read*; the distribution or shuffle key controls what is *moved*, and they are usually different columns.
- Treating bucketing as a substitute for partitioning. Buckets do not prune on a range filter; they exist to bound file count and to make joins local.
- Solving skew by adding executors. A straggler task is one key, not a capacity problem — salt it, broadcast the other side, or repartition.
- Designing layout once and never revisiting it. Volume and query patterns move, which is why partition evolution exists and why layout reviews belong in the cost cycle.

## Graph
- **Needs first:** [[file-formats]]
- **Leads to:** [[spark-tuning]], [[cost-optimization]]
- **Asked together with:** [[sql-performance-indexing]]
