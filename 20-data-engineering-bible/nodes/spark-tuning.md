---
id: spark-tuning
title: Spark Performance Tuning
tier: 1
priority: must-know
sources: [obenner/spark, obenner/hive, cookbook]
---

# Spark Performance Tuning

## Say it in one line
Tuning Spark is almost always about the shuffle: how much data crosses the network, how evenly it is spread across partitions, and whether each partition fits in a task's memory.

## Must be able to recite
- **Shuffle mechanics** — map-side tasks write partitioned, sorted files to local disk and reduce-side tasks fetch them over the network, so every shuffle costs disk, network and a stage boundary.
- **spark.sql.shuffle.partitions** — the post-shuffle partition count, default 200 regardless of data size, which is far too few for terabytes and far too many for megabytes.
- **Target partition size** — aim for roughly 128–200 MB of data per shuffle partition, which is the number you quote when asked "how did you pick the partition count".
- **Data skew** — one key holds a disproportionate share of rows, so one task runs for an hour while 199 finish in seconds and the stage takes as long as its worst task.
- **Salting** — append a random suffix `0..N` to the hot key, aggregate or join on the salted key, then re-aggregate to strip the salt; skip the second step and the answer is wrong.
- **Broadcast hash join** — ship the whole small side to every executor and join locally with no shuffle; automatic below `spark.sql.autoBroadcastJoinThreshold` (10 MB by default).
- **Sort-merge join** — the default for two large tables: shuffle both sides by the join key, sort each partition, then merge; robust but pays two shuffles.
- **Shuffle-hash join** — shuffles both sides then builds an in-memory hash table from the smaller side per partition, useful when one side is small per partition but too large to broadcast.
- **repartition vs coalesce** — `repartition` does a full shuffle and can raise or lower the count with even distribution, `coalesce` merges partitions with no shuffle but only downwards and can collapse upstream parallelism.
- **Spill** — a task's sort, aggregate or join data exceeds its execution memory and is written to local disk, which shows up in the Spark UI as spill (memory) and spill (disk) per task.
- **OOM causes** — `collect()`/`toPandas()` of a large result kills the driver, while skew, too few partitions, an exploding join or an oversized broadcast kill executors.
- **Serialisation** — Kryo is smaller and faster than Java serialisation for RDD workloads, while DataFrames use Tungsten encoders and largely bypass JVM serialisation altogether.
- **Small-files problem** — thousands of tiny input files mean one task each plus metadata pressure, so coalesce before writing and compact on read.
- **Predicate and projection pushdown** — filters are evaluated inside the Parquet/ORC reader so row groups are skipped by min/max statistics, and only projected columns are decoded at all.
- **Executor sizing and dynamic allocation** — around 5 cores and 16–32 GB per executor with ~10% memory overhead, leaving a core and a gigabyte per node for the OS; dynamic allocation then adds and removes executors by pending-task backlog, which needs the external shuffle service or shuffle tracking.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ How do you minimise data transfer / shuffling in a Spark job? — Filter and aggregate before the shuffle, broadcast the small side of a join, prefer `reduceByKey` over `groupByKey`, and enable shuffle compression.
- ★ How would you handle data skew? — Identify the hot key from the task duration spread, then salt the key, split the skewed keys into a separate broadcast join, or let AQE's skew-join handling split the partition.
- ★ repartition vs coalesce — which do you use when? — `coalesce` after a heavy filter, because it avoids a shuffle; `repartition` when you need to rebalance skew or increase parallelism, because only a shuffle redistributes rows.
- ★ How do you decide the number of partitions? — Divide the shuffled data volume by a ~128–200 MB target, keep it a multiple of total executor cores, and let AQE coalesce the tail.
- ★ Explain the join strategies Spark can pick. — Broadcast hash join when one side fits the threshold, sort-merge join for two large sorted-by-key sides, shuffle-hash join when one side is small per partition, and broadcast nested loop as the last resort for non-equi joins.
- ★ How do you do memory tuning in a Spark job? — Measure the cached size in the Storage tab first, then reduce object overhead (primitives and arrays over boxed collections, numeric keys over strings), use serialised storage levels, and only then raise executor memory.
- ★ How do you calculate executor memory and executor count? — Fix ~5 cores per executor, divide node cores by that for executors per node, split node RAM across them minus ~10% overhead and ~1 GB for the OS; the sources' worked example gives 3 executors per node and 30 for a 10-node cluster.
- ★ What causes an OutOfMemory error in Spark and how do you fix it? — Driver OOM comes from `collect`/`toPandas`, executor OOM from skew, too few partitions or a large broadcast; fix the partitioning or the skew first, because raising memory only postpones it.
- ★ What is a shuffle and which operations trigger one? — Any operation needing all values for a key in one place: `repartition`, `groupByKey`, `reduceByKey`, `cogroup`, `join`, `distinct`, and window functions.
- ★ Why prefer reduceByKey over groupByKey? — `reduceByKey` combines on the map side so only partial aggregates cross the network, while `groupByKey` moves every record and can blow up a single partition.
- ★ What is the small-files problem in Spark and how do you fix it? — Many tiny (often gzipped) files force one task per file plus decompression and metadata overhead; compact them, or `coalesce`/`repartition` before writing.
- What is spill and why does it matter? — Data that will not fit in execution memory is written to local disk mid-task; it is not an error, but heavy spill is the clearest signal that partitions are too large.
- ★ How do you read a Spark UI to find a slow job? — Open the Jobs tab, pick the longest stage, then compare max against median task duration and shuffle read size in the task summary; a big gap means skew, heavy spill means memory pressure, and the SQL tab shows which join was chosen.
- ★ How does caching help, and when does it hurt? — Cache a dataset reused by more than one action, since storage memory competes with execution memory and an oversized cache causes spill; unpersist when done.
- ★ Which serialiser do you use and why? — Kryo, because it produces smaller and faster payloads than Java serialisation, though registering classes is what makes it worthwhile; DataFrame pipelines mostly avoid the question via encoders.
- ★ What is predicate pushdown? — The engine hands the filter to the file reader so entire Parquet/ORC row groups are skipped on their min/max statistics, which is why filtering on a stored column beats filtering after the read.
- ★ How does partitioning your output files improve later queries? — Writing `partitionBy(date)` lets readers prune whole directories; over-partitioning on a high-cardinality column instead produces a small-files problem.
- ★ What is speculative execution in Spark, and does it fix skew? — It relaunches a task running much slower than the median and keeps the first to finish, which helps with a bad node but not with skew, where the duplicate is equally slow.
- What is the default parallelism, and how does it relate to partition count? — `spark.default.parallelism` (typically total executor cores) sets partitioning for RDD operations that do not inherit one, while SQL shuffles use `spark.sql.shuffle.partitions`.
- What is a Partitioner, and when would you write a custom one? — It maps a key to a partition id: hash partitioner by default, range partitioner for sorted output, and a custom one when the natural hash distributes badly.
- ★ How do you improve a join query that runs out of memory? — Broadcast the small side, or make sure the largest table is streamed rather than buffered (in Hive that is the rightmost table or a `STREAMTABLE` hint) — the sources' advice to "change RIGHT OUTER JOIN to LEFT OUTER JOIN" is not a real fix.
- What are the common mistakes developers make with Spark? — Running everything on the driver or local node instead of distributing it, calling external services once per row, and caching indiscriminately.
- How does dynamic allocation work and what does it need? — Spark requests executors while tasks are backlogged and releases idle ones; the external shuffle service (or shuffle tracking) must be on, otherwise removing an executor destroys its shuffle files.
- Why is Spark bad at many concurrent users? — An application holds its executors for its lifetime, so concurrency is a cluster-manager queueing problem; you use a shared SQL endpoint or per-team queues instead.
- How does AQE change tuning advice? — It coalesces small shuffle partitions, promotes joins to broadcast once real sizes are known, and splits skewed partitions, so hand-tuning `shuffle.partitions` matters less than it used to. *(not in sources, but standard)*
- ★ How do you trigger clean-up of accumulated metadata in a long-running job? — Split long jobs into batches and write intermediate results out (the sources also suggest `spark.cleaner.ttl`; that property was removed, ContextCleaner now handles this automatically).

## Traps
- Treating `coalesce` as a cheap `repartition` — it does not rebalance skew and it reduces upstream task parallelism, so `coalesce(1)` on a wide pipeline can serialise the whole job.
- Fixing every OOM by raising `executor-memory` — the usual root cause is a partition that is too big or too skewed, and more memory only moves the failure later.
- Judging "is this table small enough to broadcast" by file size — the 10 MB threshold is on the in-memory estimate, and a compressed 50 MB Parquet file can be several hundred megabytes once decoded.
- Leaving `spark.sql.shuffle.partitions` at 200 for every job — size it to the data or let AQE coalesce; 200 partitions over 2 TB means 10 GB per task and guaranteed spill.
- Salting a skewed key without the second aggregation — the salted result is per-salt, so you must aggregate again over the unsalted key.
- Caching everything "to make it fast" — storage memory is taken from execution memory, so unnecessary caching causes the spill it was meant to prevent.

## Graph
- **Needs first:** [[spark-core]]
- **Leads to:** [[cost-optimization]]
- **Asked together with:** [[partitioning-layout]]
