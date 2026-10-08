---
id: hadoop-hdfs
title: HDFS and Hadoop Cluster Architecture
tier: 1
priority: should-know
sources: [obenner/hadoop, cookbook]
---

# HDFS and Hadoop Cluster Architecture

## Say it in one line
HDFS is a write-once-read-many distributed filesystem that splits large files into replicated fixed-size blocks across commodity DataNodes, with one NameNode holding all the metadata in memory.

## Must be able to recite
- **HDFS design point** — optimised for high throughput on large sequential reads, not for low-latency lookups or small files, and files are append-only rather than updatable.
- **NameNode** — keeps the directory tree and the block-to-DataNode map in RAM, persisted as `fsimage` plus an `edits` log, and never stores file content.
- **DataNode** — stores blocks as ordinary local files and reports to the NameNode with a periodic heartbeat plus a block report listing everything it holds.
- **Block** — the unit of storage, 128 MB by default in Hadoop 2 and 3 (the sources say 64 MB, which was the Hadoop 1 default); a 25 MB file uses one block and only 25 MB of disk.
- **Replication factor** — 3 by default via `dfs.replication`, giving both fault tolerance and read parallelism; at factor 1 a single DataNode failure loses the data permanently.
- **Rack awareness and replica placement** — first replica on the writer's node, second on a different rack, third on another node in that second rack, so losing a whole rack still leaves a copy.
- **Secondary NameNode** — periodically merges `edits` into `fsimage` so restarts are fast; it is a checkpointer, not a standby you can fail over to.
- **HA NameNode** — an active and a standby NameNode share the edit log through a Quorum Journal Manager with ZooKeeper failover and fencing, which is what removed the single point of failure the older sources describe.
- **Federation** — several independent namespaces, each with its own NameNode, over one shared pool of DataNodes, used when metadata outgrows a single NameNode's heap.
- **Write path** — the client asks the NameNode for block locations, gets a pipeline of DataNodes, streams packets down the pipeline and receives acks back up; the block is committed once minimum replication is reached.
- **Read path** — the client gets block locations from the NameNode once, then reads directly from the nearest DataNode and verifies checksums, so the NameNode is never in the data path.
- **Safe mode** — the read-only state the NameNode holds on startup until enough block reports arrive to satisfy minimum replication, which stops it from replicating blocks it simply has not heard about yet.
- **Data locality** — the scheduler prefers node-local, then rack-local, then any placement, on the principle that moving computation is cheaper than moving data.
- **YARN** — the cluster resource layer: a global ResourceManager, a NodeManager per machine, and one ApplicationMaster per application negotiating containers; it replaced Hadoop 1's JobTracker and TaskTracker.
- **Small-files problem** — every file, directory and block costs roughly 150 bytes of NameNode heap, so millions of small files exhaust the master and create one task per tiny file; fix by compaction, `HAR`, SequenceFiles or a table format.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ What is the difference between a NameNode and a DataNode? — The NameNode holds metadata (namespace, permissions, block locations) in memory; DataNodes hold the actual blocks and report them by heartbeat and block report.
- ★ What is HDFS? — A distributed filesystem for very large files on commodity hardware, splitting each file into replicated blocks and giving streaming throughput with write-once-read-many semantics.
- ★ What happens if the NameNode crashes? — In Hadoop 1 the filesystem goes offline and you rebuild from the Secondary NameNode's checkpoint; in Hadoop 2+ HA the standby takes over automatically, so answer with both.
- ★ What is the default block size and why is it so large? — 128 MB (64 MB in Hadoop 1); large blocks keep the NameNode's metadata small and make each read a long sequential scan rather than many seeks.
- ★ What is the default replication factor and how do you change it? — 3, set by `dfs.replication` in `hdfs-site.xml` or per path with `hadoop fs -setrep -w N /path`.
- ★ Explain rack awareness and the replica placement policy. — Replicas are spread so two sit on one rack and one on another; intra-rack traffic is cheap, and cross-rack placement survives a rack or switch failure.
- ★ How much storage does a 25 MB file use? — One block, but only 25 MB of disk, because the block size is a maximum not a preallocation (the source's claim that 64 MB is consumed is wrong).
- ★ What are the two messages a DataNode sends the NameNode? — A heartbeat proving it is alive, and a block report listing every block it stores; missed heartbeats mark it dead and trigger re-replication.
- ★ What is the purpose of YARN? — It separates cluster resource management and scheduling from the processing framework, so MapReduce, Spark, Tez and others share one cluster.
- ★ What is Safe mode and why does the NameNode start in it? — It is read-only until enough block reports arrive; without it the NameNode would see under-replicated blocks that are actually fine and start needless copying.
- ★ What is the Secondary NameNode for? — It merges the edit log into `fsimage` on a schedule so the NameNode restarts quickly; it is not a backup and cannot serve traffic.
- What is a Checkpoint node and a Backup node? — A Checkpoint node fetches `fsimage` and `edits`, merges them and uploads the result; a Backup node instead keeps an in-memory namespace copy fed by a live edit stream.
- ★ What is data locality? — Scheduling the computation on the node that already holds the block, falling back to the same rack, because moving code is cheaper than moving terabytes.
- ★ Can you update a file at an arbitrary offset in HDFS? — No; HDFS is append-only with a single writer per file, so a "change" means rewriting the file or the partition.
- ★ Why does HDFS store data in blocks? — Blocks let a file exceed one disk, make replication and re-replication uniform, and give a natural unit of parallelism for readers.
- ★ What are the main components of Hadoop? — HDFS for storage, YARN for resource management, MapReduce as the original compute engine, and Hadoop Common for shared libraries.
- ★ What is the small-files problem in HDFS? — Metadata lives in NameNode RAM, so many small files exhaust the heap and produce one task per file; compact them or store them in container formats.
- ★ How does a client read from and write to HDFS? — Metadata over Hadoop RPC to the NameNode, then data streamed directly to or from DataNodes; the NameNode returns locations but never proxies the bytes.
- ★ How does the NameNode handle a DataNode failure? — Missed heartbeats mark it dead, its blocks become under-replicated, and the NameNode schedules copies from surviving replicas onto other nodes.
- What is a Balancer? — An admin tool that redistributes blocks so no DataNode is disproportionately full, typically run after adding nodes.
- What does `fsck` do in HDFS? — Reports filesystem health: block counts, under-replicated and corrupt blocks, block locations and rack topology; it does not repair the way a POSIX `fsck` does.
- What is a Block Scanner? — A per-DataNode background job that reverifies block checksums on a schedule (`dfs.datanode.scan.period.hours`) to catch silent disk corruption.
- ★ NAS vs DAS for a Hadoop cluster — Hadoop wants direct-attached storage so compute is local to data; NAS separates them and only makes sense with very high bandwidth.
- What is throughput, and how does HDFS get good throughput? — Work is split across many nodes reading their local disks in parallel, so aggregate bandwidth scales with the cluster rather than with one disk.
- Why are reads parallel but writes sequential in HDFS? — Reads hit independent replicas concurrently, whereas a write goes down a single ordered DataNode pipeline to keep the replicas consistent.
- What are the important Hadoop configuration files? — `core-site.xml`, `hdfs-site.xml`, `yarn-site.xml` and `mapred-site.xml` for site overrides, with `*-default.xml` as the read-only defaults.
- ★ What file formats can you use in Hadoop? — Text/CSV, JSON, SequenceFile, Avro, ORC and Parquet; columnar ORC or Parquet for analytics, Avro for row-wise ingestion.
- What is Hadoop Streaming? — A utility that runs any executable or script as the mapper and reducer over stdin/stdout, which is how Python mappers were written before Spark.
- What is DistCp? — A MapReduce-based tool for large inter- or intra-cluster copies, run in parallel with per-file tasks.
- What is Distributed Cache? — A mechanism to ship read-only side files (lookup tables, jars) to every node before a task starts; cached files cannot be modified or synchronised.
- What is erasure coding in HDFS? — A Hadoop 3 alternative to 3x replication with about 1.5x storage overhead, paid for with CPU on reconstruction and slower recovery. *(not in sources, but standard)*

## Traps
- Saying "the NameNode is a single point of failure" without qualification — it was in Hadoop 1 and in these sources, but HA with a Quorum Journal Manager fixed that in Hadoop 2; say which version you mean.
- Claiming a 25 MB file consumes a whole 128 MB block on disk — it consumes one block entry in metadata and 25 MB of disk.
- Calling the Secondary NameNode a backup or standby — you cannot fail over to it, only rebuild from its last checkpoint, losing whatever came after.
- Saying the client talks to the NameNode over SSH (one source says exactly this) — it is Hadoop RPC over TCP; SSH is only used to start daemons on remote hosts.
- Quoting ports 50070, 50030 and 50060 — those are Hadoop 1/2 numbers and JobTracker no longer exists; Hadoop 3 moved the NameNode UI to 9870.
- Describing JobTracker and TaskTracker as the current architecture — since Hadoop 2 that is YARN's ResourceManager, NodeManagers and a per-application ApplicationMaster.

## Graph
- **Needs first:** [[distributed-systems]]
- **Leads to:** [[mapreduce]], [[hive-impala]]
- **Asked together with:** [[file-formats]]
