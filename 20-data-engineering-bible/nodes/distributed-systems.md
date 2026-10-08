---
id: distributed-systems
title: Distributed Systems Fundamentals
tier: 1
priority: must-know
sources: [obenner/cassandra, obenner/mongo, obenner/hbase, obenner/bigtable, obenner/hadoop, obenner/sql, obenner/system-design, obenner/cdc, obenner/data-structure, devinterview, cookbook]
---

# Distributed Systems Fundamentals

## Say it in one line
A distributed system buys scale and fault tolerance by giving up a single machine's simple guarantees, so almost every design question reduces to how much consistency you sacrifice to stay available when the network breaks.

## Must be able to recite
- **CAP** — during a network partition a store must choose Consistency (every read sees the latest write) or Availability (every request still gets an answer); partition tolerance is not optional in a real cluster, so the actual choice is CP or AP.
- **PACELC** — the useful extension: if Partitioned, choose A or C; Else, in normal operation, choose Latency or Consistency. Cassandra and DynamoDB are PA/EL, HBase and Spanner are PC/EC.
- **Consistency models** — strong or linearisable (reads see the latest committed write), session guarantees (read-your-writes, monotonic reads), and eventual (replicas converge only if writes stop).
- **Quorum rule** — with N replicas, W write acknowledgements and R read acknowledgements, `R + W > N` guarantees the read set overlaps the latest write; W = N is durable but slow, W = 1 is fast but loses data.
- **Replication** — copies of the same data on several nodes for durability and read scale; the replication factor is how many copies, and a rack- or datacentre-aware placement strategy decides where they sit.
- **Leader-based versus leaderless** — MongoDB, HDFS and Kafka funnel writes through one leader per shard and fail over by election; Cassandra and Dynamo are peer-to-peer, so any node accepts a write and there is no single point of failure.
- **Sharding** — splitting different data across independent nodes by a shard key; range sharding keeps ordered scans but hotspots on monotonic keys, hash sharding spreads load but destroys range scans.
- **Consistent hashing** — keys and nodes are hashed onto one ring so adding or removing a node remaps only one arc instead of rehashing everything; virtual nodes per host even out the imbalance.
- **Consensus and leader election** — Paxos and Raft let a majority agree on one ordered log or one leader despite failures, which is also what prevents split brain (two leaders after a partition); ZooKeeper and etcd package it so other systems do not reimplement it.
- **Two-phase commit** — a coordinator asks every participant to prepare, then tells all to commit or all to roll back; atomic across nodes but it blocks if the coordinator dies, so it does not scale.
- **Saga** — instead of one distributed transaction, a chain of local transactions each with a compensating action; you trade atomicity for availability and must design the undo path.
- **Idempotency** — a retry must not change the outcome: deterministic keys with upsert or merge, dedup on primary key plus a sequence number or LSN, and immutable raw data so derived layers can be rebuilt.
- **"Exactly once" is effectively-once** — the network cannot promise single delivery, so you combine at-least-once delivery with idempotent writes and checkpoints committed together with the output.
- **LSM-tree versus B-tree** — an LSM tree buffers writes in a memtable, flushes immutable sorted files and compacts them in the background (very fast writes, read amplification, needs compaction); a B-tree updates pages in place (cheap point reads, slower random writes).
- **Write-ahead log** — every mutation is appended to a durable log before it is acknowledged, so a crashed node replays it and loses nothing; the HDFS edit log, HBase WAL/HLog and Cassandra commitlog are the same idea.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ Explain the CAP theorem — and what does it tell you when choosing a database? — Under a network partition you get consistency or availability, not both, so the real options are CP and AP; it forces you to say which failure mode you accept, stale reads or refused writes.
- ★ What is tunable consistency, and what does R + W > N mean? — The client picks a consistency level per query rather than the database picking for it; with N replicas, W write acks and R read acks, `R + W > N` guarantees the read overlaps the newest write, giving strong consistency with no leader.
- ★ How do clusters reach consensus? — Through consensus protocols such as Paxos or Raft, where a majority quorum agrees on an ordered sequence of decisions; in practice you delegate it to ZooKeeper or etcd instead of writing it yourself.
- ★ Which consistency levels exist and what does each cost? — ONE and LOCAL_ONE are fastest but may be stale, QUORUM and LOCAL_QUORUM take a majority and are the normal production setting, EACH_QUORUM needs a majority in every datacentre, ALL is strongest but one dead replica fails the request, and SERIAL gives linearisable conditional updates.
- ★ Where does MongoDB sit in CAP? — Partition-tolerant, and CP with default settings (single primary plus majority write concern); lowering the write concern or reading from secondaries shifts it toward AP and admits stale reads.
- ★ What is a replica set and how does failover work? — One primary accepts all writes, secondaries replicate and can serve reads, arbiters vote without holding data, and if the primary becomes unavailable the members elect a new one automatically.
- ★ What is replication factor, and can you change it on a live cluster? — It is the number of copies of each piece of data; you can change it while the cluster is running, but you must then run repair or rebalance so existing data actually reaches the new replica count.
- ★ How does HDFS place replicas, and what is rack awareness? — The default is three copies, two on different nodes in one rack and the third in another rack, so a rack failure cannot lose the block while cross-rack traffic stays bounded; the NameNode makes all placement decisions.
- ★ What is sharding, and what methods exist? — Distributing a dataset across machines by a shard key; MongoDB offers hashed sharding (even spread, no efficient range scans) and ranged sharding (range scans, risk of hot chunks), with `mongos` routing queries and config servers holding the chunk map.
- ★ What are the advantages of sharding? — Reads and writes scale horizontally, storage grows by adding shards, queries that include the shard key or its prefix are routed to one shard instead of broadcast, and the cluster stays partially available if a shard is down.
- ★ What is two-phase commit, and what are its phases? — Prepare, where the coordinator asks each participant to promise it can commit even after a failure, then commit, where all commit if all promised and all roll back otherwise; it guarantees a distributed transaction is all-or-nothing.
- ★ How do you make a pipeline or CDC ingest idempotent? — Write with deterministic keys through upsert or merge, dedup on primary key plus source LSN or transaction id, store checkpoints and watermarks consistently with the writes, and keep raw data immutable so derived layers can be rebuilt.
- ★ What is the role of ZooKeeper? — It holds configuration and cluster membership, provides distributed synchronisation, tracks which servers are alive through heartbeats and sessions, and pushes failure notifications so recovery can begin.
- ★ What is eventual consistency? — If no new updates are made to an item, all reads eventually return the last written value as replicas converge; until then reads may be stale, which is the price of accepting writes during a partition.
- ★ How does a write-ahead log or commit log protect a node? — Nothing is acknowledged until it is appended to the durable log, so after a crash the node replays the log to rebuild the in-memory state it had not yet flushed.
- ★ How does the system decide which node holds a key? — Either hash distribution over a ring or bucket space (Cassandra's token ring, a Redshift distribution key, a Kafka partitioner) or explicit range assignment recorded in a metadata table (HBase META, Bigtable's tablet map).
- ★ How do you choose the right storage for different data consumers? — Match access pattern to engine: point lookups by key to a key-value or wide-column store, ad-hoc aggregation to a columnar warehouse, text to a search index, replay to a log — then argue latency, consistency and cost.
- What is a heartbeat? — A periodic liveness message from worker to coordinator (DataNode to NameNode, RegionServer to ZooKeeper); a missed window marks the node dead and triggers re-replication or region reassignment.
- If data is replicated three times, is the computation also run three times? — No: the master knows which node holds each block and schedules the task there, and only if that node stops responding does it run against a replica.
- What happens with replication factor 1 and a DataNode crash? — There is no second copy, so that data is lost; RF1 is only acceptable for scratch or reproducible intermediate data.
- Is HBase strongly consistent, and what does that cost? — Yes for a row, because exactly one RegionServer owns a region at a time; the cost is that the region is briefly unavailable while it is reassigned after a failure.
- What consistency does Bigtable provide? — Strong consistency within a single cluster, since one tablet server owns each row range at a time; the source calls it eventually consistent, which is only true across the replicated clusters of a multi-cluster instance.
- Why do Cassandra, HBase and Bigtable not offer general ACID transactions? — Coordinating many rows across nodes would require consensus on every write, so they guarantee atomicity per row (Cassandra per partition, plus lightweight transactions via SERIAL) and expect you to model so one operation touches one row.
- What is a hotspot and what causes it? — All traffic landing on one node because keys are sequential or one key is disproportionately popular; range-partitioned stores split the hot range automatically, but the durable fix is a key design that spreads writes.
- Why would you not need a separate caching layer? — Cassandra's argument is that reads already come from the memtable and OS page cache with bloom filters avoiding useless disk seeks; you add Redis or Memorystore only when you need sub-millisecond reads on a small hot set.
- Explain consistent hashing. — Keys and nodes are hashed onto the same ring and a key belongs to the next node clockwise, so adding or removing a node only remaps one arc instead of rehashing every key; virtual nodes per physical host even out the distribution. (not in sources, but standard)
- LSM-tree versus B-tree — which do NoSQL stores use and why? — LSM buffers writes in memory, flushes immutable sorted files and compacts them later, giving very high write throughput at the cost of read amplification and compaction work; a B-tree updates pages in place, giving cheap point reads and slower random writes. (not in sources, but standard)
- When would you use a saga instead of two-phase commit? — When participants are independent services or stores that cannot block on a coordinator: run local transactions in sequence with a compensating action for each, accepting temporary inconsistency rather than a global lock. (not in sources, but standard)

## Traps
- Reciting "pick two of three" for CAP. Partition tolerance is not a choice in a real cluster; you are choosing C or A *during* a partition, and PACELC adds that you are choosing latency versus consistency the rest of the time.
- Saying "Cassandra is AP, therefore inconsistent". It is tunable — QUORUM reads and writes give strong consistency per query, paid for in latency and in failing when too many replicas are down.
- Treating eventual consistency as "consistent after a few seconds". It is convergence with no time bound; if you need a bound, name read-your-writes or quorum instead.
- Proposing two-phase commit for microservices or cross-cloud writes. A blocking coordinator is a single point of failure — the expected answer is idempotent writes plus a saga with compensations.
- Confusing replication with sharding. Replication copies the *same* data for durability, sharding splits *different* data for capacity, and real clusters do both.
- Claiming exactly-once processing without qualification. Delivery is at-least-once; correctness comes from idempotent writes plus checkpoints committed with the output.

## Graph
- **Needs first:** —
- **Leads to:** [[spark-core]], [[nosql-stores]]
- **Asked together with:** [[kafka-messaging]]
