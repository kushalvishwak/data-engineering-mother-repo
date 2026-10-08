---
id: observability
title: Data Observability
tier: 3
priority: should-know
sources: [obenner/observability.md, obenner/data-quality.md, obenner/system-design.md, obenner/cost-optimization.md, devinterview, cookbook]
---

# Data Observability

## Say it in one line
Data observability is knowing whether your datasets are healthy — on time, complete, unchanged in shape, plausible in value — and being able to find the cause fast; monitoring tells you the job ran, observability tells you the data is right.

## Must be able to recite
- **Monitoring vs observability** — monitoring answers questions you set up in advance about known failures (did the DAG fail, is the cluster hot), observability gives you enough signal and lineage to answer a new question such as "why is yesterday's revenue eight percent low".
- **Data vs application observability** — application observability watches request-scoped latency, error rate and traces; data observability watches dataset-scoped freshness, volume, schema and distribution over time, because data failures are silent, delayed and cumulative.
- **The five pillars** — freshness, volume, schema, distribution, lineage; the first four detect the problem, lineage scopes and explains it.
- **Freshness signal** — `max(event_time or loaded_at)` against now, compared to the dataset's promised cadence; the single cheapest signal and the first to move during an upstream outage.
- **Volume signal** — rows, bytes and partitions written per run inside an expected band; catches partial loads, an empty source file, and a rerun that doubled the batch.
- **Schema and distribution signals** — schema tracks columns added, removed, retyped or made nullable against the last known version; distribution tracks null rate, distinct count, category mix and numeric percentiles against a rolling baseline, which is what catches a re-coded status field.
- **Lineage signal** — the table- and column-level dependency graph; during an incident it gives blast radius (which dashboards and which consumers) and the upstream suspects in one hop.
- **Silent failure** — the run succeeded and the data is still wrong (missing subset, wrong join, truncation, timezone slip); only dataset-level checks and reconciliation against the source catch it, never exit codes.
- **SLI, SLO, SLA** — the SLI is the measurement ("share of days the table lands by 07:00"), the SLO is the internal target (99 percent), the SLA is the promise to the consumer with a consequence; the error budget is one minus the SLO and it is what justifies refusing a risky deploy `(not in sources, but standard)`.
- **End-to-end data SLA** — measure from source event time to availability in the serving table or BI metric, report p50 and p95 plus breach count, and attach an owner and escalation path to it.
- **What to log per run** — run id, inputs (tables, partitions, offsets, watermarks), outputs (tables, partitions, rows written), duration and resource use, retries and errors, and the data-quality result summary; this is what makes a run reproducible.
- **Logs vs metrics vs traces** — logs are discrete events with context, metrics are cheap aggregated time series with limited cardinality, traces link causally across hops; the pipeline equivalent of a trace is one run id propagated down the lineage graph.
- **Alert design** — alert on consumer-visible symptoms for tiered datasets, one named owner per alert, severity levels, suppression during known maintenance, seasonality-aware baselines, and multi-signal conditions (freshness and volume together) to cut false positives.
- **Runbook and on-call** — impact assessment, likely root causes, validation queries, mitigation, rollback or backfill steps and escalation contacts, so whoever is paged at 3am does not have to reason from scratch.
- **Cost is an observability signal** — bytes scanned, slot or cluster utilisation and cost per pipeline per day; a cost spike is usually the first visible symptom of a lost partition filter or a fan-out join.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- What is data observability? — Monitoring, alerting and diagnosing the health of datasets and pipelines — arriving on time, in the right volume, with plausible values — so that data downtime shrinks and root cause is fast to find.
- What signals would you monitor for a data pipeline? — Freshness, volume, schema change, quality-check results, run status and duration, and cost signals such as bytes scanned and cluster utilisation.
- How do you detect silent failures? — Dataset-level checks rather than job status: freshness, volume bounds, distribution shift, reconciliation against the source, plus watching a few headline business KPIs.
- How do you define and measure an end-to-end SLA for data? — From source event time to availability in the final dataset or metric, timestamped at each stage, reported as p50/p95 and breach count, with an owner and escalation path.
- ★ What is lineage and how does it help during an incident? — It maps upstream and downstream dependencies between datasets, jobs and dashboards, so you can size the blast radius, tell the right consumers, and prioritise the fix.
- How do you design alerts to avoid alert fatigue? — Make every alert actionable, scoped and owned; use severity tiers, suppression windows, seasonality-aware baselines, and prefer combined signals over one twitchy check.
- A dashboard number looks wrong — how do you debug it? — Start at the metric definition, walk the lineage to the underlying tables, check freshness and recent deploys or schema changes, then reconcile with sampling to find the layer where it diverged, and confirm whether the definition changed rather than the data.
- ★ What should you log for every pipeline run? — Inputs with offsets and watermarks, outputs with row counts, runtime and resources, warnings, errors and retries, and the quality-check summary.
- How do you run a backfill safely? — In small validated batches, off-peak, isolated from the live table (shadow table or separate partitions), rebuilding derived layers from immutable raw, with consumers warned that historical metrics will move.
- What is a runbook and what belongs in it? — Impact assessment, common root causes, validation queries, mitigation steps, rollback and backfill procedure, and escalation contacts.
- ★ What are the common incident patterns in a data platform? — Upstream outage or late data, a schema change breaking a transform, duplicates from retries, a wrong join inflating a metric, partition-boundary and timezone bugs, and cost spikes from bad queries.
- How would you design observability for a whole data platform? — Freshness, volume, quality and lineage per dataset plus run duration and failure rate per job, end to end from source to the critical BI metric, with actionable alerts and runbooks attached.
- How is data observability different from application observability? — Application observability is request-scoped and mostly synchronous; data observability is dataset-scoped and historical, so it needs baselines over time instead of instantaneous error rates.
- ★ How would you monitor an ETL process? — Track last successful run and its latency against the schedule, rows in versus rows out at each stage, the quality-check results, and alert on the consumer-visible breach rather than on every task retry.
- What is the difference between an SLI, an SLO and an SLA? — The SLI is the measurement, the SLO is the internal target for it, the SLA is the external promise with a consequence attached `(not in sources, but standard)`.
- How do you know whether a Kafka topic has been fully consumed? — Compare the consumer group's committed offset with the log end offset per partition; consumer lag at zero and stable means caught up, and rising lag is your streaming freshness alert.
- How do you monitor and control cost? — Track cost per pipeline and per team, bytes scanned per query, utilisation and storage growth by layer, watch week-over-week trend, and alert on the top movers.
- What does your first five minutes look like when a freshness alert fires at 7am? — Check whether the source and the upstream job ran, check the watermark or offset, decide hold-or-publish for the mart, tell the consumers, then diagnose.
- How do you stop an alert storm when one upstream table fails? — Alert on the root node, use lineage to suppress the dependent alerts, and page exactly one owner.
- How do you measure data downtime? — Time from when the dataset first breached to when it was correct again, split into detection time and resolution time, tracked per dataset.
- How do you know a pipeline is slow before the consumer tells you? — Track run duration as a time series per task and alert on a percentile shift, not only on absolute failure.
- What tools have you used for this? — Airflow SLAs and task alerts, dbt test results, the warehouse's query history and information schema, Prometheus with Grafana for run metrics, OpenLineage for lineage, and managed tools such as Monte Carlo or Soda `(not in sources, but standard)`.
- What is on-call for a data team? — A rotation with severity tiers, paging only for breaches on tier-one datasets, a runbook per alert, handover notes, and a blameless review after the incident.

## Traps
- Saying "we have monitoring" and meaning task success — a green run tells you the code executed, not that the numbers are right.
- Alerting on every check on every table — the channel gets muted within a week; tier the datasets and page only on a consumer-visible breach.
- Static thresholds with no seasonality — Monday is not Sunday and month-end is not mid-month, so the alert fires falsely and then gets ignored.
- An alert with no owner and no runbook — that is a notification, not observability, and it will be closed without action.
- Measuring the SLA only at the last hop — "published by 07:00" hides an ingest that ran six hours late; timestamp every stage and report p95.
- Backfilling straight into the live table — write to a shadow table or isolated partitions, validate, then swap, and warn consumers that history will change.

## Graph
- **Needs first:** [[pipeline-design]]
- **Leads to:** —
- **Asked together with:** [[data-quality]], [[orchestration-airflow]]
