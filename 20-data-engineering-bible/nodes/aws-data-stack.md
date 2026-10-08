---
id: aws-data-stack
title: AWS Data Stack
tier: 2
priority: must-know
sources: [obenner/aws, obenner/redshift, obenner/airflow, cookbook]
---

# AWS Data Stack

## Say it in one line
The AWS data stack is S3 as the lake, Glue as the catalogue and serverless Spark, Athena or Redshift as the query engine, EMR for heavy Spark, Kinesis for streams, and Step Functions or MWAA to sequence it.

## Must be able to recite
- **S3** — Object store with eleven nines of durability that is the single source of truth for the lake, so every engine reads one copy and storage is already separate from compute.
- **S3 storage classes** — Standard, Intelligent-Tiering, Standard-IA, One Zone-IA, Glacier Instant/Flexible Retrieval and Deep Archive (the source's list including Reduced Redundancy is dated; RRS is deprecated).
- **Glue Data Catalog** — The Hive-compatible metastore that Athena, EMR, Redshift Spectrum and Glue jobs all share, so one table definition serves many engines; crawlers can infer it, but production tables get explicit DDL.
- **Glue ETL job** — Serverless Spark billed in DPU-hours, with job bookmarks tracking what has already been processed for incremental runs.
- **Athena** — Serverless Trino over S3 billed per terabyte scanned, so its cost is decided entirely by partitioning, columnar format and column selection.
- **EMR** — Managed Hadoop/Spark clusters where you control the version and the tuning; use transient per-job clusters with spot task nodes, or EMR Serverless to skip sizing altogether.
- **Redshift** — MPP warehouse with one leader node planning and compute nodes scanning; RA3 keeps data in S3-backed managed storage and Redshift Serverless bills RPU-seconds.
- **Redshift Spectrum** — External tables over S3 queried from Redshift and joinable to local tables in one statement, so cold history never has to be loaded.
- **COPY and UNLOAD** — COPY is the only sane bulk load into Redshift because it reads many S3 files in parallel across slices; UNLOAD writes query results back out to S3.
- **Kinesis Data Streams vs Firehose** — Streams is a shard-based durable log you consume yourself with replay inside the retention window; Firehose is a managed delivery pipe that buffers and writes to S3, Redshift or OpenSearch with no consumer code.
- **Lambda** — Event-driven functions capped at 15 minutes, correct for per-file or per-record work and wrong for large joins or shuffles.
- **Step Functions vs MWAA** — Step Functions is a serverless state machine that orchestrates AWS service calls with built-in retries and error paths; MWAA is managed Airflow, and it is what most AWS data teams actually schedule real DAGs with.
- **DMS** — Migrates and then continuously replicates operational databases, with a full-load phase followed by CDC read from the source's transaction log.
- **Lake Formation** — A central permissions layer over the Glue catalogue giving database, table, column and row-level grants that Athena, Redshift and EMR honour, instead of hand-written bucket policies.
- **The reference pipeline** — DMS or Kinesis lands into S3 raw, Glue or EMR Spark writes partitioned Parquet to S3 curated, the Glue catalogue exposes it, Athena serves ad hoc and Redshift serves BI, with MWAA or Step Functions driving the schedule.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ What is Amazon Redshift and why is it popular among cloud data warehouses? — A fully managed petabyte-scale MPP warehouse that gets its speed from columnar storage, compression and parallel scans across compute nodes, and is priced far below a traditional on-premise appliance.
- ★ What is the difference between a leader node and a compute node? — The leader node parses SQL, builds and distributes the execution plan and aggregates the final result; compute nodes hold the data slices, run their part of the plan and return partial results.
- ★ What is Redshift Spectrum and how does it work? — Redshift compiles and optimises the query, then pushes scans and predicates down to the Spectrum layer, which reads Parquet/JSON/Avro directly from S3; the S3 tables can be joined to local Redshift tables in the same query.
- ★ How do you load data into Redshift, and what is the recommended way for large volumes? — COPY from S3 (also DynamoDB, EMR or SSH), splitting the input into multiple files or using a manifest so every slice loads in parallel; row-by-row INSERT is the classic mistake.
- ★ What are distribution keys and sort keys in Redshift? — The distribution key decides which slice a row lands on and therefore whether a join is local or has to redistribute; the sort key sets on-disk order and drives zone-map block skipping.
- ★ What is the difference between VACUUM and ANALYZE? — VACUUM reclaims space from deleted rows and restores sort order; ANALYZE refreshes the statistics the optimiser plans with. Modern Redshift runs both automatically, so the right answer is "automatic, and I monitor it".
- ★ Which AWS services would you use to collect and process e-commerce data for real-time analysis? — Kinesis Data Streams (or MSK) for ingestion, Managed Flink or Lambda for processing, DynamoDB or OpenSearch for low-latency serving, and S3 plus Redshift for analytics (the source answers "DynamoDB then Redshift", which is not a streaming design — Kinesis is the missing piece).
- ★ What is S3 and how do you send a request to it? — A pay-as-you-go object store you read and write over a REST API or an SDK wrapper; there is no filesystem underneath, only keys and prefixes.
- What storage classes does S3 offer and how do you use them for a lake? — Standard for hot partitions, Intelligent-Tiering when access is unpredictable, Standard-IA and Glacier tiers for history, driven by a lifecycle rule on the prefix rather than by hand.
- ★ How does Redshift work with AWS Glue for cataloguing and ETL? — Glue crawls or is told about S3 data and registers it in the Glue Data Catalog, which Spectrum reads as external schemas, while Glue jobs run the Spark transforms that produce the curated tables.
- ★ How does Athena fit alongside Redshift? — Athena runs ad hoc SQL straight over S3 with no cluster and per-TB billing, so it covers exploration and one-off analysis, while Redshift holds modelled, indexed, concurrency-managed tables for BI.
- How do you use Kinesis Data Firehose for real-time ingestion into Redshift or S3? — Producers write to Firehose, which buffers by size or time, optionally converts to Parquet and invokes a Lambda for transformation, then delivers to S3 (and stages via S3 into Redshift).
- ★ How do you orchestrate an AWS data pipeline? — Step Functions for service-call workflows with retries and error branches, or MWAA/Airflow when you need DAGs, backfills, sensors and a scheduler; Lambda handles the small event-driven glue.
- How would you use Lambda in a data pipeline? — For serverless reactions to events: validate or convert a file as it lands in S3, kick off a Glue job or COPY, or enrich small records before load, within the 15-minute limit.
- ★ How do you manage query concurrency and workload isolation in Redshift? — WLM queues with concurrency limits and priorities, short-query acceleration, and concurrency scaling to add transient capacity when queries start queueing.
- What is AWS Lake Formation used for? — Central, catalogue-level access control for the lake with column and row-level permissions and tag-based grants, so Athena, Redshift and EMR all enforce the same rules.
- What is DMS and when do you use it? — AWS Database Migration Service performs a full load of a source database and then keeps replicating changes from its transaction log, which is how operational data reaches S3 or Redshift continuously (not in sources, but standard).
- What is EMR and when do you pick it over Glue? — EMR is a managed Hadoop/Spark/Hive/Presto cluster you control; pick it when you need specific engine versions, heavy long-running jobs or fine tuning, and Glue when you want serverless Spark with no cluster to manage.
- ★ How do you secure data in Redshift and S3? — Encryption at rest with KMS-managed keys, TLS in transit, IAM roles rather than credentials for COPY/UNLOAD, VPC placement with PrivateLink, and audit logging to CloudTrail and to Redshift's own logs.
- Can you query semi-structured JSON or Avro in Redshift? — Yes, via Spectrum over S3 files, or with `SUPER` columns and `PartiQL` inside Redshift for nested data.
- Can you create materialized views and UDFs in Redshift? — Yes to both, and Redshift can rewrite queries to use a materialized view automatically (the source says no to both; that was true years ago and is now wrong).
- ★ What is DynamoDB, and when does a data engineer use it? — A serverless NoSQL key-value/document store with single-digit-millisecond latency at any scale and its own autoscaling; use it for high-volume operational lookups and serving layers, not for analytics scans.
- What is Redshift Federated Query? — Querying live data in RDS, Aurora PostgreSQL/MySQL from Redshift SQL, which avoids a copy for small reference or operational tables.
- ★ What is CloudWatch used for? — Metrics, logs and alarms across AWS services, which is where you watch cluster CPU, queue depth, Lambda errors and Redshift query performance.
- ★ What is the relation between availability zones and regions in AWS? — A region is a set of AZs, and an AZ is a physically separate data centre; put a Redshift or RDS standby in a second AZ so an infrastructure failure does not take the service down.
- What is the purpose of a standby RDS instance? — It sits in a different availability zone and takes over on failure via synchronous replication, so an infrastructure failure in one AZ is survivable.
- What are spot and on-demand instances, and where do they belong in a data platform? — Spot is reclaimable spare capacity at a steep discount and belongs on EMR task nodes and retryable backfills; on-demand or reserved runs the driver, core nodes and anything with a tight SLA.
- What is Snowball used for? — Physically shipping terabytes into or out of AWS when the network would take too long; it is the answer to "how do you migrate 500 TB from an on-premise warehouse".
- What is the maximum size of a Redshift cluster and of a table? — Up to 128 RA3 compute nodes on the largest node type, with per-table limits in the tens of terabytes and 1,600 columns; treat these as quota trivia and check the current docs rather than quoting 2021 numbers.
- Can you restore a Redshift snapshot to another region? — Yes, by enabling cross-region snapshot copy and restoring from the copy (the source says no; that is wrong).

## Traps
- Reciting EC2, Route 53 and CloudFront when asked about the AWS *data* stack: the panel wants S3, Glue, Athena, Redshift, Kinesis and an orchestrator, and certification trivia signals you have not built anything.
- Describing Athena as cheap or fast without conditions: it bills per terabyte scanned, so an unpartitioned CSV lake makes it both slow and expensive, and the fix is Parquet plus a partition predicate.
- Confusing Kinesis Data Streams with Firehose: if you say Firehose and then talk about replaying from an offset you have lost the point, because Firehose has no consumer offsets.
- Treating Glue crawlers as the schema source of truth: one malformed file changes an inferred column type and silently breaks every downstream query.
- Reaching for Lambda for real transformation work: the 15-minute timeout and memory cap mean that job belongs in Glue or EMR Spark.
- Repeating old limitations — "Redshift has no materialized views, no UDFs, no cross-database queries, you cannot change a sort key" — all four are wrong today, and stale facts cost more credibility than gaps.

## Graph
- **Needs first:** [[cloud-fundamentals]]
- **Leads to:** [[warehouse-engines]]
- **Asked together with:** [[pipeline-design]]
