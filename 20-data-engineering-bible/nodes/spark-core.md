---
id: spark-core
title: Spark Core Concepts
tier: 1
priority: must-know
sources: [obenner/spark, obenner/hadoop, cookbook]
---

# Spark Core Concepts

## Say it in one line
Spark is a distributed compute engine that turns a lazy DAG of transformations over partitioned data into stages of tasks and runs them in memory across executors.

## Must be able to recite
- **Driver** — runs your `main()` and owns the SparkSession, builds the DAG and schedules tasks, so if it dies the whole application dies.
- **Executor** — a long-lived JVM on a worker node that runs tasks and holds cached partitions for the lifetime of the application.
- **Cluster manager** — the pluggable layer that hands out containers for driver and executors: YARN, Kubernetes or standalone (the sources also list Mesos; that is deprecated since Spark 3.2 and removed in Spark 4).
- **Job / stage / task** — one action is one job, every shuffle boundary cuts that job into stages, and each stage runs one task per partition.
- **RDD** — an immutable partitioned collection of records with lineage but no schema, so Catalyst cannot optimise it.
- **DataFrame** — a `Dataset[Row]` with named columns, which is what lets Catalyst and Tungsten rewrite your query; it is the only structured API in PySpark.
- **Dataset** — typed JVM objects with compile-time type safety through encoders, available in Scala and Java only.
- **Transformation vs action** — transformations are lazy and return a new dataset, while actions (`count`, `collect`, `write`) are the only things that launch a job.
- **Narrow vs wide dependency** — narrow means one parent partition feeds one child partition (`map`, `filter`), wide means data is redistributed by key, which is a shuffle and a new stage.
- **Lazy evaluation** — nothing executes until an action, which is precisely what lets the optimiser push filters down and prune columns before any data moves.
- **Catalyst and Tungsten** — Catalyst rewrites the logical plan and picks a physical plan, then Tungsten executes it with off-heap binary rows and whole-stage code generation.
- **AQE (Adaptive Query Execution)** — re-plans mid-query using real shuffle statistics, coalescing small partitions and switching join strategies; on by default since Spark 3.2.
- **cache, persist, checkpoint** — `cache()` is `persist()` with a default level (`MEMORY_ONLY` for RDDs, `MEMORY_AND_DISK` for DataFrames), whereas `checkpoint()` writes to reliable storage and truncates lineage.
- **Accumulators and broadcast variables** — accumulators are executor-write/driver-read counters, broadcast variables ship one read-only copy per executor instead of one per task.
- **Structured Streaming** — the DataFrame API over an unbounded input table, executed as micro-batches with checkpoint plus write-ahead log for exactly-once output; it supersedes DStreams.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ Explain the Spark architecture / runtime components. — A driver builds the DAG and schedules work, a cluster manager allocates containers, and executors run tasks on partitions and cache data; the driver never touches the data itself.
- ★ How does a DAG become tasks? — The DAG scheduler splits the lineage graph at shuffle boundaries into stages, the task scheduler then launches one task per partition per stage through the cluster manager.
- ★ Difference between RDD, DataFrame and Dataset. — RDD is untyped-schema records with no optimiser, DataFrame adds a schema so Catalyst can optimise, Dataset adds compile-time typing on top of DataFrame in Scala/Java.
- ★ What is an RDD? — An immutable, partitioned, distributed collection that records its lineage so any lost partition can be recomputed rather than replicated.
- ★ How is a Dataset type-safe? — Encoders map JVM objects to Tungsten's binary format, so column and type errors fail at compile time instead of at run time.
- ★ Transformations vs actions, with examples. — `map`, `filter`, `join`, `groupBy` are transformations and build the plan; `count`, `collect`, `take`, `write` are actions and force execution.
- ★ What is lazy evaluation and what do you gain from it? — Transformations only record intent, so Spark sees the whole pipeline at action time and can fuse operators, push filters into the scan and avoid materialising intermediates.
- ★ Narrow vs wide transformations, and which operations shuffle? — `groupByKey`, `reduceByKey`, `join`, `distinct`, `repartition` and `coalesce`-with-shuffle are wide; anything that needs all values of a key in one place is a shuffle.
- ★ Why is Spark faster than MapReduce? — Spark keeps intermediate results in memory and runs the whole pipeline as one DAG, while MapReduce writes every job's output to HDFS and pays JVM start-up per task.
- ★ What is a shuffle? — An all-to-all redistribution of data across partitions: map-side tasks write partitioned files to local disk and reduce-side tasks fetch them over the network.
- ★ cache() vs persist()? — Same mechanism; `persist` lets you name the storage level, `cache` uses the default, and both are lazy so nothing is stored until the next action.
- What are the storage/persistence levels? — `MEMORY_ONLY`, `MEMORY_AND_DISK`, the `_SER` serialised variants, `DISK_ONLY`, and `_2` replicated variants; serialised levels trade CPU for space.
- Does Spark support checkpointing, and when do you use it over caching? — Yes; use it when lineage is long or has wide dependencies, because recomputing a 50-stage lineage after a failure costs more than one write to reliable storage.
- ★ What is a broadcast variable and when would you use one? — A read-only value cached once per executor, used to send a lookup table or the small side of a join without shipping it with every task.
- ★ What is an accumulator? — A variable executors can only add to and the driver reads, used for counters and metrics; only trust it inside actions, since a retried task can double-count in transformations.
- ★ Client mode vs cluster mode. — In cluster mode the driver runs inside the cluster (use it for production and for remote clients); in client mode the driver runs on the submitting machine, which is convenient for shells but dies with that machine.
- ★ What is YARN, and must Spark be installed on every node? — YARN is Hadoop's resource manager that allocates containers to Spark; no, you do not install Spark on each node because the application jars are shipped to the containers.
- ★ What is a partition, and how many do you get reading from HDFS? — A partition is the unit of parallelism and one task processes one partition; by default you get one partition per HDFS block, and you can ask for more but not fewer at read time.
- ★ What is RDD lineage and how does it give fault tolerance? — Every dataset remembers the transformations that built it, so Spark recomputes only the lost partition instead of replicating data the way HDFS does.
- ★ What is Spark SQL? — A module that runs SQL and the DataFrame API on the same Catalyst engine, reads Hive tables through the metastore, and is reachable over JDBC/ODBC.
- ★ What is Structured Streaming, and how does it differ from the old Spark Streaming? — Structured Streaming treats the stream as an unbounded DataFrame on the SQL engine with event-time windows and exactly-once sinks; DStreams were an RDD-level micro-batch API and are now legacy.
- ★ What are micro-batches? — The stream is cut into small time-sliced batches, each executed as an ordinary Spark job, which gives batch semantics and throughput at the cost of latency.
- Tumbling vs sliding windows. — Tumbling windows are fixed and non-overlapping so each event lands in one window; sliding windows advance by less than their width, so an event can appear in several.
- ★ What is Parquet and why is it the default for Spark? — A columnar, compressed, self-describing format; Spark reads only the columns you project and skips row groups using min/max statistics.
- Parquet vs Avro. — Parquet is columnar and made for analytical reads; Avro is row-based with a compact schema, better for write-heavy ingestion and schema evolution.
- ★ What is SparkContext / SparkSession? — The entry point that connects to the cluster manager and owns the job scheduler; SparkSession (Spark 2.0+) wraps SparkContext, SQLContext and HiveContext into one object.
- Do you need HDFS to run Spark? — No; Spark reads any supported filesystem or connector, including S3, ADLS, GCS, local files, JDBC, Cassandra and Kafka.
- ★ What are Spark's limitations? — No storage layer or built-in file management, memory-hungry, weak on many small files, and poor at true per-record low latency compared with Flink.
- ★ Can Spark and Hadoop be used together? — Yes, and normally they are: HDFS or S3 for storage, YARN for scheduling, and the Hive metastore for the catalogue.
- What is SchemaRDD? — The pre-1.3 name for what is now a DataFrame (the sources still call it SchemaRDD; that API no longer exists).
- How do you get high availability for the Spark master? — In standalone mode, run standby masters coordinated by ZooKeeper; under YARN or Kubernetes the resource manager already handles it.
- What does AQE actually change at runtime? — It coalesces too-many small shuffle partitions, converts a sort-merge join to a broadcast join once it sees the real side size, and splits skewed partitions. *(not in sources, but standard)*

## Traps
- Saying Datasets give "run-time type safety" because a source says so — the entire point is compile-time safety, and there is no Dataset API in PySpark at all.
- Reciting "Spark is 100x faster than MapReduce" as a flat fact — that figure is for iterative in-memory workloads; on a single-pass, disk-bound scan the gap is small, and interviewers push on exactly this.
- Treating `cache()` as immediate — it is a lazy hint, so nothing is in memory until the next action, and an evicted partition is silently recomputed.
- Confusing checkpointing with persisting — persist is an optimisation that may be evicted, checkpoint is a durable write that also cuts lineage.
- Naming Mesos as a current cluster manager — say YARN or Kubernetes; Mesos support was deprecated in 3.2 and removed in Spark 4.
- Claiming an accumulator is safe anywhere — task retries and speculative execution can apply an update twice unless it is inside an action.

## Graph
- **Needs first:** [[distributed-systems]]
- **Leads to:** [[spark-tuning]]
- **Asked together with:** [[mapreduce]], [[batch-vs-streaming]]
