---
id: nosql-stores
title: NoSQL Stores and Data Modelling
tier: 1
priority: must-know
sources: [obenner/cassandra, obenner/mongo, obenner/hbase, obenner/bigtable, obenner/aws, obenner/hive, obenner/impala, devinterview, cookbook]
---

# NoSQL Stores and Data Modelling

## Say it in one line
NoSQL stores give up joins, enforced schemas and cross-row transactions in exchange for horizontal scale and predictable latency, so you design the physical layout around the queries you already know you will run.

## Must be able to recite
- **Key-value** — a hash map at cluster scale: get and put by key, with no querying inside the value. Redis, DynamoDB. Sessions, caches, feature flags, rate limiting.
- **Wide-column** — rows addressed by a row key, columns grouped into families, sparse and schema-optional. Cassandra, HBase, Bigtable. Time-series, IoT telemetry, clickstream and event logs, per-customer ledgers.
- **Document** — self-describing JSON/BSON documents in collections, with secondary indexes and an aggregation pipeline. MongoDB, CouchDB. Product catalogues, user profiles, content whose shape varies.
- **Graph** — nodes and edges where traversal is the primary operation. Neo4j. Fraud rings, entitlement chains, recommendations, KYC relationship discovery — queries that become unbounded self-joins in SQL.
- **Query-first design** — you create the tables the queries need, one per access pattern, and duplicate data deliberately, because there are no joins and no foreign keys to rescue you later.
- **Partition key versus clustering key** — Cassandra's partition key hashes to a node and must appear in every query; the clustering columns sort rows inside that partition and are what give you range scans and ordering.
- **Partition sizing** — keep a Cassandra partition under roughly 100 MB and 100,000 rows, so a bare `customer_id` partition key eventually becomes a hotspot and needs a bucket such as `(customer_id, month)`.
- **Tombstones** — because SSTables are immutable, a delete writes a marker that hides the value and the data disappears only at compaction; accumulated tombstones slow reads and cause timeouts.
- **Embed versus reference (Mongo)** — embed when the child is read with the parent and bounded, reference when the data is shared, unbounded or updated independently; keep nesting to two or three levels and remember the 16 MB document cap.
- **Mongo indexes and the ESR rule** — order compound index fields Equality, then Sort, then Range; indexes must fit in RAM to be fast, and every index taxes every write.
- **Aggregation pipeline** — an ordered chain of stages (`$match`, `$group`, `$sort`, `$lookup`) where each stage's output feeds the next; Mongo's stand-in for `GROUP BY` and the occasional join.
- **Row-key design (HBase, Bigtable)** — the row key is the only index and rows are stored sorted, so it must encode the access pattern; a monotonic key (timestamp, sequence id) sends every write to one region, fixed by salting or reversing the prefix and by pre-splitting regions.
- **Tall-thin versus short-wide** — put the varying dimension in the row key (tall) for range scans and selective reads, or in columns (wide) when you always read the whole entity and the column count is small.
- **DynamoDB keys and GSIs** — the primary key is a partition key plus an optional sort key; a Global Secondary Index is a separately keyed asynchronous copy of the table, so it is eventually consistent and provisioned separately.
- **When not to use NoSQL** — ad-hoc joins across entities, cross-entity transactions, enforced referential integrity, or unknown query patterns on a dataset one relational box can hold; for analytics the answer is a columnar warehouse, not a document store.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ How many types of NoSQL database are there — name one example and one use case each? — Key-value (Redis, Voldemort) for caches and sessions; wide-column (Cassandra, HBase, Bigtable) for time-series and event logs; document (MongoDB, CouchDB) for profiles and catalogues; graph (Neo4j, Giraph) for relationship traversal such as fraud rings.
- ★ How do you model a table in Cassandra? — Query first: enumerate the access patterns, then build one table per pattern with a partition key that every query supplies and clustering columns for the required order and ranges, duplicating data across tables instead of joining.
- ★ What is the difference between a partition key and a clustering key? — Together they form the primary key: the partition key determines which node holds the row and must be in the `WHERE` clause, while the clustering columns sort rows inside the partition and enable range queries and `ORDER BY`.
- ★ What is a key-value or row store versus a column store? — A key-value store returns an opaque value for a key with no querying inside it; a column store keeps each column's values together so you can scan and aggregate a few columns across many rows.
- ★ What is a document store? — A store of self-contained JSON or BSON documents grouped into collections, where documents in one collection may have different fields and nested structures are queried directly.
- ★ How does Cassandra write, and what are the commitlog, memtable and SSTable? — The write is appended to the commitlog on disk and applied to the in-memory memtable before it is acknowledged; when the memtable fills it is flushed to an immutable SSTable, and each SSTable also gets a partition index, summary and bloom filter.
- ★ What is a tombstone and why does it matter? — SSTables are immutable, so a delete writes a special marker that makes the value invisible; the data is only reclaimed at compaction, and a build-up of tombstones degrades reads and causes query timeouts.
- ★ What is compaction, and what is the difference between minor and major? — Compaction merges SSTables or HFiles to cut the number of disk seeks per read; minor compaction runs automatically on similarly sized files, major compaction is triggered manually, merges everything for a column family and discards deleted data.
- ★ What is a bloom filter and why do these stores use one? — An off-heap probabilistic structure that cheaply answers "this key is definitely not in this file", so the store skips disk I/O for SSTables or HFiles that cannot contain the key.
- ★ What is hotspotting, and how do you avoid it? — A disproportionate share of client traffic hitting one node or region, overwhelming that machine and potentially making the region unavailable; avoid monotonic row keys, salt or reverse the key prefix, and pre-split regions before bulk loads.
- ★ Do HBase and Cassandra support joins? — No. You denormalise so the join is unnecessary, or you run the join in the application or in a MapReduce/Spark/Hive job across the tables.
- ★ What is a row key in HBase, and what is its scope? — Application-defined bytes that prefix every cell key and therefore set the sort order; all cells with the same row key are co-located on one server, and the same row key can exist in every column family without collision.
- ★ What is a column family and why does it matter physically? — It is the basic unit of physical storage and configuration — compression, block size, version count, TTL are set per family — so access patterns that differ should not share one.
- ★ How does HBase differ from an RDBMS? — Schema-less and denormalised rather than schema-bound and normalised, column-oriented and sparsely populated rather than row-oriented and thin, partitioned automatically rather than manually, and indexed only on the key column.
- ★ How does HBase delete a row, and what are the three tombstone marker types? — It writes a delete marker rather than removing data: a version marker hides one version of a column, a column marker hides all versions of a column, and a family marker hides every column in a family; major compaction removes them.
- ★ When would you use HBase? — When you need random real-time reads and writes at high throughput over tables with billions of rows and millions of columns, want strong per-row consistency, and already run the cluster to support it.
- ★ What is the difference between Hive and HBase? — Hive is a SQL-like batch warehouse layer over HDFS that compiles to MapReduce; HBase is a NoSQL key-value store on HDFS answering real-time row operations. They complement each other and data moves both ways.
- ★ Why do you pre-create empty regions? — A new table starts as a single region, so a bulk load writes to one region until it is large enough to split; pre-splitting spreads the load across the cluster from the first write.
- ★ What is the difference between Bigtable and HBase? — Essentially the same data model, since HBase was built from the Bigtable paper and its HFile is modelled on Bigtable's SSTable; the difference is that Bigtable is a managed Google service and HBase is self-operated on Hadoop.
- ★ Describe Bigtable's data model. — A sparse, distributed, multidimensional sorted map indexed by row key, column key and timestamp, with values stored as uninterpreted bytes; rows are range-partitioned into tablets served by tablet servers.
- ★ Does Bigtable support secondary indexes? — No, it relies entirely on row-key design; you either encode the access pattern in the key or maintain a second table that acts as your index.
- ★ What is the impact of schema design on Bigtable performance? — It dominates everything: row-key design and column-family configuration decide whether a read is a single-tablet scan or a full sweep, and whether writes spread or hotspot.
- ★ How does MongoDB store data and how does it differ from an RDBMS? — As documents in compressed BSON inside collections, so a collection maps to a table, a document to a row and a field to a column, but with nested structure and no enforced schema.
- ★ What are the best practices for MongoDB schema design? — Model on the query patterns, embed related data read together, reference data that is shared or unbounded, keep nesting to two or three levels, index the common queries, plan for document growth, and version the schema.
- ★ Where should you index in MongoDB and how do you choose a strategy? — On fields your repeated queries filter and sort on, ordered Equality then Sort then Range, selective enough to narrow the result, small enough to fit in RAM, and dropped when unused because every index slows every write.
- ★ What is the aggregation pipeline? — An ordered set of stages where each stage transforms documents and passes them to the next — filter, group, compute, sort — producing grouped and aggregated results without SQL.
- ★ How does atomicity work in MongoDB? — A write is atomic on a single document including its embedded documents; a multi-document update is atomic per document but not as a whole, so you need an explicit distributed transaction — hence the rule "embed what must change together".
- ★ What are MongoDB's limitations? — Limited joins, a 16 MB document cap, no foreign-key constraints, higher storage from duplicated denormalised data, and integrity pushed into application code.
- ★ How does MongoDB handle large data volumes? — Sharding for throughput and capacity, targeted indexes, the aggregation pipeline for processing, WiredTiger compression, GridFS for large files, and capped or time-series collections for high-volume append data.
- ★ When would you choose Cassandra? — When you need multi-datacentre writes with no single point of failure, linear write scale-out on commodity nodes and tunable consistency, on a workload whose queries are known up front; its original use case was Facebook inbox search.
- Does Cassandra support ACID transactions? — Not relationally: you get atomic, isolated writes per partition and lightweight compare-and-set transactions at SERIAL, but nothing across partitions, so the source's flat "no" overstates it slightly.
- What is DynamoDB, and what are its partition keys and GSIs? — A fully managed NoSQL service with no cluster to operate; the primary key is a partition key plus an optional sort key, and a Global Secondary Index is a separately keyed asynchronous copy, therefore eventually consistent and charged separately.
- What are HBase's disadvantages versus an RDBMS? — No built-in authentication or permission model in the early versions, indexes only on the key column, and a single HMaster as a point of failure (dated — HBase elects standby HMasters through ZooKeeper, so that is a deployment choice).
- What is TTL, and how do these stores expire data? — A retention period after which a version is dropped at compaction, configured per column family or cell in HBase; Bigtable does the same through garbage-collection policies, so the source's claim that Bigtable has no automatic expiration is wrong.
- ★ What kinds of query are best suited to HBase rather than a warehouse? — Those where you would reach for a key-value store: fetching one row or a handful of rows by testing a unique key with `=` or `IN`, not scanning and aggregating across the table.
- Does Bigtable support change data capture? — The source says no; that is outdated — Bigtable change streams have been generally available since 2023 and are consumed with Dataflow or the client libraries.
- ★ When should you *not* use NoSQL? — When you need ad-hoc joins, cross-entity transactions and enforced referential integrity, or when the query patterns are still unknown on data small enough for one relational server; for reporting and analytics the answer is a columnar warehouse.

## Traps
- Saying "NoSQL means no schema". It means no schema enforced by the database — the schema moves into your application and every consumer, and Cassandra is in fact stricter about it than Mongo.
- Designing a Cassandra table like a relational one, then discovering you cannot filter on a non-key column. Every query must supply the partition key; `ALLOW FILTERING` is a warning, not a feature.
- Using an incrementing timestamp or sequence id as a row key. Every write lands on one region or node — bucket, salt or reverse the key.
- Deleting heavily in Cassandra and considering the row gone. Tombstones persist until compaction and are a leading cause of read timeouts, so prefer TTLs and partition-level deletes over per-row churn.
- Embedding an unbounded array in a Mongo document. Documents cap at 16 MB and growth forces rewrites; switch to a reference once the child set can grow without limit.
- Answering "NoSQL because it scales" in a bank scenario. Name the access pattern instead: high-volume point lookups by key, yes; regulatory reporting, joins and ad-hoc analytics, no — that is a warehouse.

## Graph
- **Needs first:** [[distributed-systems]], [[oltp-vs-olap]]
- **Leads to:** [[warehouse-engines]]
- **Asked together with:** [[system-design-scenarios]]
