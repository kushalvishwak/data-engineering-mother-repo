---
id: warehouse-engines
title: Warehouse Engines Compared
tier: 2
priority: must-know
sources: [obenner/redshift, obenner/bigquery, obenner/greenplum, obenner/aws, cookbook]
---

# Warehouse Engines Compared

## Say it in one line
Every cloud warehouse is columnar and massively parallel; they differ in whether compute is a cluster you size (Redshift, Synapse, Greenplum), a warehouse you resume (Snowflake), or invisible (BigQuery).

## Must be able to recite
- **MPP shared-nothing** — A coordinator plans the query and N workers each scan the slice of data they own in parallel, so throughput scales with nodes only while the data stays evenly distributed.
- **Columnar storage** — Values of one column are stored together, so a query reads only the columns it names and compresses far better; this is why warehouses win on aggregates and lose on single-row lookups.
- **Coupled vs decoupled compute** — Classic Redshift DC/DS nodes and Synapse dedicated pools hold data on the compute nodes, so resizing moves data; RA3, Snowflake and BigQuery keep data in object storage, so compute can be resized, paused or duplicated freely.
- **Snowflake virtual warehouse** — A named, resizable (XS to 6XL), independently billed compute cluster; several warehouses read the same data, so ETL and BI stop competing, and per-second billing with auto-suspend means idle costs nothing.
- **Snowflake micro-partitions** — Immutable chunks of roughly 50–500 MB of uncompressed data created automatically on load, each carrying per-column min/max metadata used for pruning; you never declare partitions, only an optional clustering key.
- **Snowflake time travel and zero-copy clone** — Time travel queries or restores data up to 1 day back on Standard and 90 days on Enterprise; `CLONE` creates a table, schema or whole database that shares the same micro-partitions with no data copied, which is how you get instant dev environments.
- **Redshift distribution styles** — KEY co-locates rows sharing a value (use the big fact's join key), ALL replicates a small dimension to every node, EVEN round-robins, AUTO lets Redshift decide; a wrong choice appears as a broadcast or redistribute step in `EXPLAIN`.
- **Redshift sort key and zone maps** — The sort key sets on-disk order, and per-block min/max zone maps let scans skip blocks entirely, so the leading sort column should be the one you filter by range (usually the date).
- **Redshift VACUUM vs ANALYZE** — VACUUM reclaims space from deleted rows and restores sort order, ANALYZE refreshes optimiser statistics; both now run automatically, so the answer is "automatic, and I monitor whether it is keeping up".
- **Redshift RA3, Spectrum and Serverless** — RA3 caches hot blocks locally over S3-backed managed storage, Spectrum queries S3 external tables in the same SQL statement, and Serverless removes node sizing and bills RPU-seconds.
- **BigQuery's difference** — No nodes, no distribution keys, no vacuum: the only levers are partitioning, clustering, column selection and slot reservations.
- **Synapse dedicated SQL pool** — MPP over 60 distributions with HASH, ROUND_ROBIN and REPLICATE distributions and DWU sizing you can scale and pause; the closest analogue to Redshift.
- **Greenplum** — PostgreSQL-derived on-premise MPP with a coordinator, mirrored segments and the Interconnect, `DISTRIBUTED BY`/`RANDOMLY`/`REPLICATED`, and resource queues for workload management; you meet it at banks with pre-cloud warehouses.
- **Workload management** — Every engine has a version — Redshift WLM queues, Snowflake multiple warehouses plus resource monitors, BigQuery reservations, Synapse resource classes, Greenplum resource queues — and the point of all of them is stopping one heavy query from starving the rest.
- **Concurrency scaling** — Redshift concurrency scaling and Snowflake multi-cluster warehouses spin up transient clusters when queries queue, which absorbs the 9 a.m. dashboard spike without paying for it all day.

| Engine | Compute model | What you tune | Pick it when |
|---|---|---|---|
| Snowflake | Per-second virtual warehouses with auto-suspend | Warehouse size, one warehouse per workload, clustering keys | You want zero operations, hard workload isolation and the same platform on any cloud |
| BigQuery | Fully serverless slots, no cluster at all | Partitioning, clustering, column selection, reservations | You are on GCP and want no capacity decision to make, and can live with per-TB or slot-pool billing |
| Redshift | Provisioned RA3 nodes, or Serverless RPUs | Distribution keys, sort keys, WLM, concurrency scaling | You are deep in AWS and want tight S3/Glue/Spectrum integration and reserved-node pricing |
| Synapse dedicated pool / Fabric | DWUs you scale and pause explicitly | Distributions, replicated dimensions, COPY INTO loads | The estate is Microsoft end to end and Power BI is the consumption layer |
| Greenplum | Fixed on-premise MPP cluster | Distribution keys, table partitions, resource queues | Data cannot leave the data centre, or you inherited a Pivotal/EMC warehouse and must keep it alive |

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ Which data warehouse would you pick, and why? — Name the deciding factors rather than a favourite: which cloud the data already sits in, whether you need workload isolation, whether load is spiky or flat, who will operate it, and how the vendor bills; then commit to one and state the trade-off you accepted.
- ★ What is columnar storage and why does it matter in a warehouse? — Data is stored column by column, so a query reads only the columns it references and compresses far better because neighbouring values are similar; the result is much less IO for aggregate queries.
- ★ How does an MPP warehouse achieve scalability? — Columnar storage plus distributing the data and the query across many compute nodes that scan their slices in parallel, so adding nodes adds throughput as long as distribution stays even.
- ★ What is a distribution key and what is a sort key, and how do you choose them? — The distribution key decides which node or slice a row lives on and therefore whether joins are local; the sort key decides on-disk order and lets block-level metadata skip data. Distribute on the high-cardinality join key, sort on the column you filter by range.
- Can you change the sort key or distribution key of an existing table? — Yes: `ALTER TABLE ... ALTER SORTKEY`, `ALTER DISTKEY` and `ALTER DISTSTYLE` all exist, and Automatic Table Optimization can change them for you (the source says you must recreate the table; that has been out of date since 2019).
- ★ What is the difference between a leader node and a compute node? — The leader parses SQL, produces and distributes the plan and assembles the final result; compute nodes store the slices, execute their portion and return partials.
- ★ What is the difference between VACUUM and ANALYZE, and what do the VACUUM options do? — VACUUM reclaims space and restores sort order (`DELETE ONLY` reclaims only, `SORT ONLY` re-sorts only, `REINDEX` rebuilds interleaved sort keys); ANALYZE updates the statistics the planner uses. There is no standalone `REINDEX` command in Redshift, despite what the source claims.
- ★ What is separation of storage and compute, and which engines have it? — Data lives in object storage while stateless compute attaches on demand; BigQuery, Snowflake and Redshift RA3/Serverless have it, while classic Redshift DC/DS nodes and Synapse dedicated pools store data on the compute nodes.
- ★ How do you manage query concurrency and stop one query ruining the cluster? — Workload management: queues with concurrency and memory limits and priorities in Redshift, a separate virtual warehouse per workload in Snowflake, slot reservations in BigQuery, resource classes or queues in Synapse and Greenplum, plus query timeouts everywhere.
- ★ Can a warehouse be used as an OLTP database? — No: these engines are built for large scans with columnar storage and no per-row indexes, so single-row lookups and high-frequency small writes belong in PostgreSQL, Aurora or DynamoDB.
- ★ How does the warehouse optimiser handle a star schema join? — It uses statistics, distribution and sort metadata to filter the dimensions first and then probe the fact table, so the fact table's distribution key and the freshness of `ANALYZE` statistics decide whether the join is local or shuffled.
- ★ How does Greenplum's architecture work? — A coordinator receives and plans the query, the Query Dispatcher sends slices to segments that each hold part of the data, segments exchange rows over the Interconnect, and mirrored segments with automatic failover provide high availability.
- ★ What distribution strategies does Greenplum support? — `DISTRIBUTED BY (key)` for hash distribution, `DISTRIBUTED RANDOMLY` for even spread with no join locality, and `DISTRIBUTED REPLICATED` for small tables copied to every segment (the source lists "random, even and key-based"; "even" is Redshift's term, not Greenplum's).
- ★ How do you detect and fix data skew in an MPP warehouse? — Compare row counts and disk use per slice or segment; the fix is a better distribution key, a surrogate/salted key, replicating the small side, or letting the engine redistribute for that one join.
- ★ How does a warehouse handle materialized views? — It stores the pre-computed result and refreshes it incrementally, and both Redshift and BigQuery can rewrite a query on the base tables to use it automatically (the source says Redshift has no materialized views; that is wrong, they have been generally available since 2020).
- ★ What is Redshift Spectrum and why does it matter? — External tables over S3 queried from Redshift and joinable to local tables in one statement, so cold history stays in cheap object storage while hot, modelled data stays in the cluster.
- ★ How do you load large volumes into an MPP warehouse? — Bulk-load in parallel from object storage: `COPY` in Redshift, `COPY INTO`/PolyBase in Synapse, `COPY`/Snowpipe in Snowflake, load jobs in BigQuery, `gpfdist`/external tables in Greenplum. Serial `INSERT` statements are the standard failure.
- ★ How does the engine handle compression? — Per-column encodings chosen by the data's shape (run-length, delta, dictionary, byte-dictionary, Zstandard), applied automatically on load in modern engines, which reduces both storage and the bytes each scan reads.
- ★ What happens when a compute node or segment fails? — The engine fails over to a mirror or replacement node and rebuilds from managed storage or snapshots; queries in flight fail and retry, which is why loads must be idempotent.
- What is a Snowflake virtual warehouse? — An independently sized and billed compute cluster that reads the shared storage layer; you run separate warehouses for loading, transformation and BI so they never contend, and auto-suspend stops the meter when idle (not in sources, but standard).
- What are Snowflake micro-partitions and clustering keys? — Snowflake automatically splits tables into immutable ~50–500 MB micro-partitions with per-column min/max metadata for pruning; a clustering key tells it to keep those partitions sorted on a column when natural load order is not selective enough (not in sources, but standard).
- What are Snowflake time travel and zero-copy cloning? — Time travel lets you query or restore a table as of an earlier point within the retention window, and `CLONE` creates a new object sharing existing micro-partitions with no data copy, so a full-size dev environment is instant and nearly free (not in sources, but standard).
- How do you choose the right store for different data consumers? — Match the access pattern: warehouse for modelled SQL analytics, lake plus a query engine for exploratory and semi-structured data, key-value or wide-column store for low-latency lookups, search index for text, cache for repeated hot reads.
- ★ How do you resize a cluster, and can you do it while it is running? — Yes: elastic resize adds or removes nodes in minutes, classic resize rewrites the data and takes longer, Snowflake resizes a warehouse instantly for new queries, and BigQuery has nothing to resize.
- ★ How does the warehouse handle backup, snapshots and point-in-time recovery? — Automated snapshots to object storage on a retention schedule, plus manual snapshots you keep, restore to a new cluster, and in Snowflake and BigQuery a time-travel window that covers accidental deletes without a restore.
- ★ How do you secure a cloud warehouse? — Encryption at rest with customer-managed keys and TLS in transit, IAM/role-based access down to column and row level, network isolation with private endpoints, and audit logging of every statement.
- ★ Can these engines query semi-structured data? — Yes: `SUPER`/PartiQL in Redshift, `VARIANT` in Snowflake, STRUCT/ARRAY in BigQuery, JSON functions in Greenplum and Synapse, plus external tables over Parquet, Avro and JSON in object storage.
- Can you create indexes in a columnar warehouse? — Not in the OLTP sense; sort keys, clustering keys, zone maps and micro-partition metadata do the equivalent job of skipping data you do not need.
- Can you create UDFs and stored procedures? — Yes in all of them (Redshift supports SQL, Python and Lambda UDFs plus PL/pgSQL procedures, so the source's "no UDFs" answer is wrong).
- What is the difference between Greenplum and PostgreSQL? — Greenplum is built on PostgreSQL but distributes tables across segments for parallel analytical scans, adds columnar and compressed storage and resource queues, and gives up the single-node transactional performance PostgreSQL is tuned for.
- What are the advantages of Greenplum over Hive or Impala? — Full ANSI SQL with real transactions, a mature cost-based optimiser and predictable performance without a Hadoop cluster (the source calls it open source; Broadcom stopped publishing source for new releases in 2024, so treat it as a vendor-licensed product now).
- What are the limitations of a serverless warehouse like BigQuery? — Cost is driven by bytes scanned so a careless query is expensive, there are quotas on DML and streaming, large schema changes mean rewriting the table, and you cannot tune the physical layout beyond partitioning and clustering.

## Traps
- Calling Snowflake serverless: its compute is a virtual warehouse that you or auto-resume start, and it bills while running — BigQuery is the genuinely serverless one.
- Swapping the definitions of distribution key and sort key: distribution decides which node holds the row (join locality), sort decides the order within the node (scan pruning). Interviewers ask this to see if you have actually tuned a cluster.
- Choosing the date column as the Redshift DISTKEY: every day's load then lands on one slice, so distribute on the high-cardinality join key and sort on the date instead.
- Repeating old limitations — no materialized views, no UDFs, no cross-database queries, sort keys are immutable, snapshots cannot cross regions — every one of those is now false, and stale facts read worse than admitting you have not used the product.
- Comparing engines on benchmark numbers: the panel wants trade-off reasoning about isolation, elasticity, pricing model, ecosystem fit and who operates it.
- Forgetting that all of them are poor at OLTP: if the scenario needs single-row reads at millisecond latency or thousands of small updates per second, say so and put an operational database in front.

## Graph
- **Needs first:** [[warehouse-architecture]], [[cloud-fundamentals]]
- **Leads to:** [[cost-optimization]]
- **Asked together with:** [[sql-performance-indexing]]
