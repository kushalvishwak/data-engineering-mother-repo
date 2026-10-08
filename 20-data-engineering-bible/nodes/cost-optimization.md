---
id: cost-optimization
title: Cost Optimisation
tier: 2
priority: should-know
sources: [obenner/cost-optimization, obenner/bigquery, obenner/redshift, obenner/aws, obenner/gcp, obenner/spark, obenner/system-design]
---

# Cost Optimisation

## Say it in one line
In a cloud data platform the bill is a design output: it is set by how many bytes each query touches, how long compute stays switched on, and how much data you keep, duplicate and move.

## Must be able to recite
- **The four cost drivers** — Compute time (clusters, warehouses, slots), bytes scanned and shuffled, storage growth across raw plus derived plus duplicates, and data movement (egress and cross-region transfer).
- **Pricing models** — Per-second or per-hour compute, per-terabyte-scanned query pricing, per-GB-month storage, per-request serverless, and commitment discounts; each one rewards a different optimisation.
- **Partition pruning** — The engine skips whole partitions when the filter matches the partition column, which is the largest single lever in a lake or warehouse; a partition column nobody filters on buys nothing.
- **Over-partitioning and small files** — Too many partitions produces the small-files problem, where metadata and planning overhead exceed the scan work, so target a few hundred megabytes per file and compact.
- **Columnar format plus projection pushdown** — Parquet or ORC combined with naming only the columns you need cuts bytes read directly, which is why `SELECT *` in a lake query is a bill rather than a style issue.
- **Right-sizing** — Measure actual CPU, memory and slot utilisation and size to the normal case, then autoscale or use a separate larger cluster for the worst hour instead of running the worst hour all day.
- **Spot / preemptible capacity** — Reclaimable spare capacity at 60–90% off, safe for retryable Spark task nodes and backfills, unsafe for drivers, databases and streaming jobs with tight SLAs.
- **Reserved / committed / savings plans** — A one- or three-year commitment to baseline capacity for a large discount, with the spiky top of the curve left on-demand; commit only to the floor you have actually measured.
- **Storage tiering and lifecycle rules** — Automatic transitions from Standard to Infrequent Access to Archive by age, plus expiry for staging and log data; check retrieval fees and minimum storage durations before tiering data anyone still reads.
- **Query cost controls** — Per-query and per-user byte limits, query timeouts, `require_partition_filter`, workload queues with concurrency caps, and budget alerts; guardrails hold where training does not.
- **Separate compute per workload** — Give ETL, ad hoc and BI their own warehouse, queue or reservation so one cross join cannot slow the morning load, and so cost can be attributed to a team.
- **Materialise deliberately** — Pre-compute the marts that many dashboards reuse and keep exploratory logic as views, because every materialisation is storage plus a refresh job forever.
- **Stop recomputing history** — Incremental and CDC loads instead of full reloads, with idempotent partition overwrites so a rerun costs one partition rather than the whole table.
- **Backfill planning** — Measure throughput on one small window, extrapolate, then run staged and off-peak with a kill switch; unplanned backfills are the classic surprise on a month-end bill.
- **FinOps metrics** — Cost per pipeline, team and dataset, bytes scanned per query, cluster and slot utilisation, storage growth by layer, and the ten most expensive queries week over week, each tied to who consumes the output.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ How do you manage cost while still meeting SLAs? — Optimise the layout first (partitioning, file sizes, columnar formats), avoid recomputation with incremental loads and selective materialisation, move heavy jobs off-peak, enforce quotas per team, and track cost per dataset so the trade-off is explicit rather than discovered.
- Why is cost optimisation a core data engineering skill? — Data platform cost scales with volume and usage, often faster than linearly, so a design that ignores cost stops being affordable exactly when the data becomes valuable.
- What are the main cost drivers in a data platform? — Compute time, bytes scanned and shuffled, storage growth including derived and duplicated copies, data movement and egress, and operational overhead from retries and repeated backfills.
- ★ How does partitioning affect cost and performance? — Good partitioning lets the engine prune whole partitions and read a fraction of the data; bad partitioning creates thousands of tiny partitions whose metadata and planning overhead costs more than the scan it saved.
- What is the small files problem and why does it increase cost? — Each file adds open, list and planning work, so the engine spends more time on metadata than on data; it comes from streaming writes and over-granular partitions, and the fix is compaction or clustering.
- How do you choose a target file size for Parquet tables? — Balance parallelism against per-file overhead, typically a few hundred megabytes per file, adjusted to the engine's split size and how selective the queries are.
- ★ How do you monitor and optimise warehouse query cost? — Read the query history and plans, use `INFORMATION_SCHEMA`/system tables for bytes scanned, slot-milliseconds and duration per query, export billing data, set budgets and alerts, and attack the top ten most expensive queries first.
- ★ How do you prevent runaway queries and protect a shared cluster? — Query timeouts, concurrency and memory limits per queue, byte limits per query and per user, separate compute for heavy workloads, plus cost alerts and linting so the guardrail exists before the incident.
- ★ What is the difference between on-demand and reserved capacity pricing, and when do you buy each? — On-demand bills per terabyte scanned or per hour with no commitment and suits spiky or unknown workloads; reserved slots, nodes or commitments discount a measured steady baseline, so you buy the floor and leave the peak on-demand.
- ★ Where do spot or preemptible instances belong in a data platform? — On stateless, retryable compute such as EMR/Dataproc task nodes and large backfills, where losing a node just reruns a task; never on the driver, a database, or a streaming job whose SLA does not tolerate interruption.
- ★ How do you reduce shuffle, and why does it matter for cost? — Shuffle redistributes data across the network for joins, group-bys and distincts and is where time and money go; filter early, select only needed columns, broadcast the small side, partition on the join key, and tune the shuffle partition count.
- ★ How do you detect and fix data skew? — Look at task duration and partition size distributions for stragglers; fix with salted keys, skew-aware or broadcast joins, repartitioning, or handling the hot keys separately.
- ★ How do you optimise joins in large-scale analytics? — Clean and evenly distributed join keys, filter and project before joining, choose broadcast versus shuffle deliberately, and pre-join into a curated mart when the same join runs many times a day.
- ★ When should you pre-aggregate or materialise a table? — When many downstream queries reuse the same expensive computation, or when interactive BI needs low latency; stop when the refresh cost and storage exceed the query savings, and keep exploratory logic as views.
- How do you plan and estimate the cost of a backfill? — Run one representative window, measure bytes processed, runtime and cost, extrapolate across the range, then stage it off-peak with monitoring and a documented rollback.
- What metrics would you track for FinOps in data engineering? — Cost per team, project, pipeline and dataset; bytes scanned per query; cluster and slot utilisation; storage growth per layer; the most expensive datasets and queries; and week-over-week trend, always tied to how much the output is actually used.
- ★ How do you optimise storage cost specifically? — Lifecycle rules into colder tiers, partition-level expiry, deleting abandoned tables and old table versions, letting untouched partitions fall to long-term storage pricing, and not keeping three derived copies of the same raw data.
- ★ How do you optimise storage inside a warehouse? — Correct per-column compression encodings, `VACUUM`/compaction to reclaim deleted-row space, refreshed statistics so the planner reads less, and dropping the staging tables nobody cleaned up.
- ★ How do you control BigQuery cost specifically? — Partition and cluster on the columns queries filter on, set `require_partition_filter`, never `SELECT *`, use the free query cache and materialized views, set custom byte quotas per project and per user, and reserve slots once usage is predictable.
- How do you control cost in a provisioned cluster warehouse? — Pause or shut down what nobody is querying (a Synapse dedicated pool and a Redshift cluster both bill while idle), scale down out of hours, use concurrency scaling or a serverless option for spikes, and reserve nodes only for the steady baseline.
- ★ How do you monitor and analyse cloud spend? — Enable billing export to the warehouse, tag or label every resource with team and pipeline, build a cost dashboard on the export, and set budgets with alerts rather than reading last month's invoice.
- ★ How do you optimise data ingestion cost? — Batch instead of streaming unless there is a latency requirement (batch loads are usually free, streaming is not), compress in transit, and land in a columnar format so nothing has to be rewritten later.
- ★ How does cross-region or egress traffic show up on the bill? — Reading across regions or out to the internet is charged per gigabyte and is easy to trigger accidentally with a badly placed bucket, cluster or BI tool; keep storage and compute in the same region.
- What is the cost impact of choosing the wrong file format? — Row-based CSV or JSON forces the engine to read every column and cannot compress well, so switching a hot table to Parquet or ORC often cuts scanned bytes by an order of magnitude.
- ★ How do you right-size a Spark or EMR cluster? — Look at real executor CPU and memory utilisation, spill and GC time, then match executor size and count to the partition count; over-provisioning shows up as idle executors and under-provisioning as spills and retries.
- What is the cost of over-materialising? — Every materialised table adds storage plus a refresh job that runs whether anyone reads it, so unused marts are a recurring charge; find them by joining usage logs to the table list and drop what nobody queries.

## Traps
- Repeating "the cloud is cheaper": it is cheaper for spiky and short-lived work and often more expensive for a flat 24/7 workload without commitments, and a bank interviewer who has seen the migration bill knows it.
- Optimising storage first: storage is usually a few percent of a data platform's bill, while compute and bytes scanned are where the money actually is.
- Adding a partition column for every query pattern: you get thousands of tiny partitions, and both cost and latency go up — partition on one coarse column and cluster or sort for the rest.
- Buying reserved capacity to fix a cost spike: a commitment locks in the bad baseline, so find and fix the runaway job first and only then commit to the floor.
- Answering with tool names instead of numbers: say what you measured (bytes scanned, utilisation, cost per run) and what changed after, because "we enabled tiering" is not an optimisation story.
- Cutting cost without naming the trade-off: the question is "manage cost *while meeting SLAs*", so the strong answer states which freshness, latency or retention you renegotiated and with whom.

## Graph
- **Needs first:** [[cloud-fundamentals]], [[warehouse-engines]]
- **Leads to:** —
- **Asked together with:** [[partitioning-layout]], [[spark-tuning]]
