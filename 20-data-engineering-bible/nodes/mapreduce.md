---
id: mapreduce
title: MapReduce
tier: 1
priority: should-know
sources: [obenner/hadoop, obenner/spark, cookbook]
---

# MapReduce

## Say it in one line
MapReduce is a batch model where you write two functions — map, which turns each input record into key-value pairs, and reduce, which aggregates all values for a key — and the framework handles the split, shuffle, sort and fault tolerance in between.

## Must be able to recite
- **The five phases** — split, map, shuffle, sort, reduce; you write only map and reduce, and everything between them is framework-managed.
- **InputSplit** — the logical slice of input one mapper processes, one per HDFS block by default, so the number of splits determines the number of mappers.
- **Block vs split** — a block is physical storage in HDFS, a split is a unit of work; a record straddling a block boundary is stitched back together by the RecordReader.
- **Map output location** — intermediate key-value pairs are written to the mapper node's local disk, never to HDFS, and are deleted when the job finishes.
- **Shuffle** — each reducer fetches its own partition from every mapper's output over HTTP, which is the only network-heavy phase of the job.
- **Sort** — the framework merge-sorts the fetched map output by key so each `reduce()` call receives one key and an iterator of all its values; sort overlaps with the fetch.
- **Reduce** — writes final output to HDFS, one file per reducer, and that output is not re-sorted afterwards.
- **Combiner** — an optional map-side mini-reducer that pre-aggregates before the shuffle, valid only when the operation is commutative and associative and its input and output types match the map output types.
- **Partitioner** — decides which reducer each key goes to, `HashPartitioner` by default (`key.hashCode() mod numReduceTasks`), so the number of partitions equals the number of reducers.
- **Speculative execution** — the framework launches a duplicate attempt of a task running far slower than the median and keeps whichever finishes first, which hides a bad node but does nothing for skew.
- **Counters** — framework and user-defined counters aggregated back to the client, used to validate record counts and count bad records without a second job.
- **Reducer count** — the rule of thumb is `0.95` or `1.75 × (nodes × reduce slots)`: 0.95 gives one wave, 1.75 gives two waves and better load balancing.
- **Zero reducers is legal** — map output then goes straight to HDFS unsorted, which is how map-only jobs (filters, format conversion, DistCp) work.
- **Map-side vs reduce-side join** — a map-side join needs the small side to fit in memory (or both sides bucketed and sorted on the key) and skips the shuffle; a reduce-side join works for any size but pays a full shuffle.
- **Why Spark replaced it** — MapReduce materialises every job's output to HDFS and starts a fresh JVM per task, so an iterative or multi-step pipeline pays a disk round-trip per step; Spark expresses the whole pipeline as one in-memory DAG.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ Walk me through a MapReduce job end to end. — Input is split, one mapper per split emits key-value pairs to local disk, the partitioner assigns each key to a reducer, reducers fetch and merge-sort their partition, then `reduce()` runs per key and writes to HDFS.
- ★ Write pseudocode for word count. — `map(key, line): for w in line.split(): emit(w, 1)` and `reduce(w, counts): emit(w, sum(counts))`, with the same function registered as combiner.
- ★ What is a combiner and when can you use one? — A map-side pre-aggregation that cuts shuffle volume; only valid when the operation is commutative and associative, so `sum` and `max` are fine but `average` is not unless you emit sum and count.
- ★ What is the difference between a combiner and a reducer? — A combiner sees the output of one mapper only and its types must match the map output, while a reducer sees all mappers for its keys and may emit different types.
- ★ How does partitioning work, and how do you send a key to a specific reducer? — The partitioner maps each key to a partition id and there is one reducer per partition; extend `Partitioner` and override `getPartition()`, then set it with `job.setPartitionerClass()`.
- ★ What is the difference between a block and a split? — A block is how HDFS stores bytes, a split is how much one mapper reads; by default they coincide, but a split is a logical range that can cross a block boundary mid-record.
- ★ What are the phases of the reducer? — Shuffle (fetch map output), sort (merge by key), reduce (call `reduce()` per key); shuffle and sort overlap.
- ★ Where does mapper output get stored? — On the mapper node's local disk, in spilled and merged partition files; only reducer output goes to HDFS.
- ★ What is speculative execution? — A duplicate attempt for a straggler task, with the loser killed; it protects against slow hardware, not against a task with genuinely more data.
- ★ How many mappers and reducers will your job have? — Mappers equal the number of input splits and you influence that only via split size and file layout; the reducer count you set directly with `setNumReduceTasks`.
- ★ What happens if you set the number of reducers to zero? — Legal and common: map output is written straight to HDFS with no shuffle and no sorting.
- ★ Why is Spark preferred over MapReduce? — No per-job HDFS materialisation, one DAG instead of chained jobs, in-memory reuse for iterative work, and a far shorter API; MapReduce is now legacy in almost every shop.
- ★ Is there any value in learning MapReduce if Spark exists? — Yes: the map-shuffle-sort-reduce model is exactly what Spark's stages do, and skew, spill and partitioning arguments all transfer directly.
- ★ When is MapReduce not the right tool? — Iterative algorithms, interactive queries and anything with many chained steps, because each step persists to disk and pays start-up cost again.
- ★ What is the difference between a map-side and a reduce-side join? — Map-side loads the small table into memory on each mapper and joins with no shuffle; reduce-side sends both tables through the shuffle keyed on the join column.
- ★ What are the core methods of a Mapper and a Reducer? — `setup()` once per task, `map()`/`reduce()` per record or per key group, `cleanup()` once at the end, with `run()` driving the loop.
- ★ What is the Context object used for? — It carries configuration into the task and is how you emit output, update counters, report progress and set status messages.
- ★ Why do we need serialisation in MapReduce? — Keys and values cross process and machine boundaries, so Hadoop uses `Writable` serialisation to convert objects to a compact binary form and back.
- What are counters used for? — Counting records processed, bad records skipped or business events, all aggregated centrally so you get a job-level number without a separate aggregation job.
- What is an identity mapper and identity reducer? — Defaults that pass their input through unchanged, used when you only want the framework's sort and partition behaviour.
- What is a chain mapper? — Several mappers run in sequence inside one map task, each feeding the next, so you avoid writing intermediate output between them.
- Is Java mandatory for MapReduce? — No; Hadoop Streaming runs any executable over stdin/stdout and Hadoop Pipes exposes a C++ API.
- What is a RecordReader? — The component that turns a split's raw bytes into key-value pairs for `map()`, and that handles records spanning a block boundary.
- What is `isSplitable()`? — A per-input-format flag; set it false for formats that cannot be read from an arbitrary offset (for example non-splittable gzip), so the whole file becomes one split.
- ★ What is data locality in MapReduce? — The scheduler tries to run each mapper on a node holding its block, then in the same rack, to avoid reading over the network.
- Can reducers talk to each other? — No; tasks are isolated by design, which is what lets the framework retry or duplicate any task freely.
- ★ What is a use case for MapReduce? — Large one-pass batch aggregation over raw files: log and clickstream summarisation, ETL format conversion, and index building.
- How is a MapReduce job scheduled and monitored? — Under YARN the client submits to the ResourceManager, which starts an ApplicationMaster that requests containers and tracks task attempts (the sources describe JobTracker and TaskTracker; that is Hadoop 1 only).
- Which schedulers does Hadoop offer? — FIFO, Capacity Scheduler and Fair Scheduler; Capacity is the common production choice for multi-tenant queues.
- How do you control the split size? — Through `mapreduce.input.fileinputformat.split.minsize` and `.maxsize` against the block size, since split size is `max(minsize, min(maxsize, blocksize))`.

## Traps
- Assuming the combiner always runs exactly once — the framework may run it zero, one or several times per mapper, so its logic has to be safe under all three.
- Using a combiner for a non-associative aggregate like average — emit `(sum, count)` pairs and finish the division in the reducer instead.
- Saying "you set the number of mappers" — you only influence it through split size and file count; the reducer count is the one you set directly.
- Saying mapper output is written to HDFS — it goes to local disk, which is why a lost mapper node forces a re-run of that map task.
- Claiming speculative execution solves skew — a duplicate of a task with ten times the data is equally slow; skew needs repartitioning or salting.
- Describing JobTracker and TaskTracker as current — that is MRv1; on any Hadoop 2+ cluster it is YARN with a per-application ApplicationMaster.

## Graph
- **Needs first:** [[hadoop-hdfs]]
- **Leads to:** [[spark-core]]
- **Asked together with:** [[distributed-systems]]
