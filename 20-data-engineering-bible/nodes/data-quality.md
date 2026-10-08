---
id: data-quality
title: Data Quality
tier: 3
priority: must-know
sources: [obenner/data-quality.md, obenner/observability.md, obenner/system-design.md, obenner/dbt.md, devinterview, cookbook]
---

# Data Quality

## Say it in one line
Data quality is whether the data is fit for its intended use, expressed as automated tests over six dimensions — completeness, validity, accuracy, consistency, timeliness, uniqueness — that run inside the pipeline and can stop a bad load before anyone sees it.

## Must be able to recite
- **The six dimensions** — completeness (rows and fields present), validity (values in the allowed domain), accuracy (agrees with source or real-world truth), consistency (no contradiction across tables), timeliness/freshness (arrives inside the SLA), uniqueness (no duplicates on a key); accuracy is the only one that needs an external reference.
- **Validation vs reconciliation** — validation asks "does this dataset obey its own rules", reconciliation asks "does it still agree with the source system"; a table can pass every validation and still be short by twelve rows.
- **Row-level vs aggregate checks** — row-level judges each record (not-null, regex, range, allowed values), aggregate judges the dataset (row count, distinct count, sum, distribution); a whole missing partition passes every row-level check.
- **Freshness check** — `max(event_time or loaded_at)` against now, compared to a per-dataset SLA; the cheapest single check and the first thing to reveal an upstream outage.
- **Volume / anomaly check** — rows written per run inside an expected band or against a seasonality-aware baseline; catches partial loads and duplicated reruns that no row rule can see.
- **Uniqueness on the business key** — compare `count(*)` with `count(distinct business_key)`, never the surrogate key, which is unique by construction and hides join fan-out.
- **Referential-integrity check** — every foreign key in the fact resolves to a row in the dimension; warehouses accept but do not enforce PK/FK, so this orphan test is the only real guard.
- **Distribution check** — null rate, category mix and numeric percentiles against recent history; catches silent semantic change such as a currency switch or a re-coded status field.
- **Reconciliation against source** — compare control totals (row count, `sum(amount)`, counts per business date) between source extract and warehouse table at the same watermark; in banking this is the check the business actually asks for, and it runs on the money columns.
- **Where the tests belong** — contract and schema checks at ingest, row-level checks plus quarantine in staging, uniqueness/referential/reconciliation after transform, freshness/volume/key-metric checks as the gate before publish; only the publish gate must block.
- **Fail fast vs quarantine** — fail fast stops the load and keeps the mart internally consistent, quarantine routes rejected rows with an error reason into a side table and lets good rows through; choose by consequence, money fails fast and optional enrichment gets quarantined.
- **Data contract** — a versioned, machine-readable agreement on schema, types, nullability, semantics, freshness SLA and owner, enforced in the producer's CI; it converts a 6am surprise into a failed build.
- **Schema-drift policy** — additive columns allowed by policy, renames and type narrowing fail fast, enforced by comparing the incoming schema to the expected one or by a schema-registry compatibility rule.
- **Idempotency is a quality control** — `MERGE` on a deterministic key, or delete-and-reinsert the whole partition, so a retry cannot double-count; without it "duplicates from retries" becomes your top failure mode.
- **Tooling actually asked** — dbt tests (generic `unique`, `not_null`, `accepted_values`, `relationships`, singular tests that must return zero rows, and `dbt source freshness`), with Great Expectations or Soda when the checks must live outside the warehouse `(not in sources, but standard)`.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ How do you ensure data quality in a pipeline? — Name the six dimensions, then the concrete test at each layer, then the failure policy (block publish vs quarantine) and who gets alerted; never answer "I check the data".
- What is the minimum set of checks you would put on every table? — Freshness, row-count band, uniqueness on the key, not-null on critical columns, and referential integrity on the join keys.
- What are the dimensions of data quality? — Completeness, validity, accuracy, consistency, timeliness, uniqueness.
- How would you reconcile the warehouse against the source system? — Agree a control total per batch (row count and sum of a money column per business date) at a fixed watermark, write both sides to a break table, and alert on any non-zero difference.
- What is the difference between data validation and data reconciliation? — Validation tests rules inside one dataset; reconciliation compares totals or invariants between two systems that can drift apart.
- ★ How do you detect duplicates and how do you prevent them? — Detect with `count(*)` versus `count(distinct business_key)` per partition; prevent with idempotent writes rather than hoping retries behave.
- What is data freshness and how do you measure it? — Latest event or load timestamp against now, judged by a cadence agreed per dataset; alert on SLA breach, not on absolute lag.
- ★ How do you design quality checks for an incremental pipeline? — Scope the checks to the new window (uniqueness within the batch, batch size in bounds) and still assert table-level invariants such as the total moving by the expected amount.
- What is a silent failure and how do you catch it? — The job is green but the data is wrong (missing subset, wrong join, truncation); only dataset-level checks — volume, distribution, reconciliation, headline metric — catch it.
- How do you handle late-arriving data? — Declare an allowed lateness, track completeness by event time rather than ingestion time, and reprocess the affected historical partitions in a controlled backfill.
- How do you detect schema drift and breaking changes? — Compare the incoming schema against the contract (names, types, nullability) on every run, allow additive change, fail fast on rename or type narrowing.
- What are data contracts? — An explicit producer-to-consumer agreement on schema, semantics, SLA and ownership, kept as code so it can be enforced in CI instead of discovered in production.
- How do you avoid noisy alerts and false positives? — Seasonality-aware thresholds, multi-signal conditions (freshness and volume together), severity by dataset criticality, suppression during maintenance, and an owner plus runbook on every alert.
- How do you quarantine bad data without blocking the whole pipeline? — Split the output into good and quarantine sets with the rejection reason attached, keep publishing valid rows, but hold the mart if the rejected share crosses a threshold.
- ★ How do you test a data transformation? — Golden fixtures with expected output, invariant tests (no negative totals), reconciliation against the source, and regression tests on headline metrics; in dbt these run as SQL assertions in the warehouse.
- ★ What are the common data quality failure modes? — Missing or partial partitions, retry duplicates, schema drift and type coercion, timezone and date-boundary bugs, silent truncation or rounding change, and join fan-out inflating measures.
- What is anomaly detection on a metric and when is it worth it? — Statistical bands on a KPI to flag unexplained spikes and drops; it is the tool for silent failures, but without release and campaign context it becomes noise.
- Row-level or aggregate checks — which catch more? — Aggregate checks find the expensive failures (missing partition, volume collapse, metric inflation) that row-level rules structurally cannot see.
- ★ Why does a staging layer help quality? — It is where you validate, clean and deduplicate before anything reaches the target, and it lets you re-run the transform without re-extracting the source.
- ★ Full load or incremental load — which is safer for quality? — Full reload is simple and self-correcting but expensive; incremental is cheap but needs a reliable change marker plus duplicate and completeness checks.
- Who owns data quality? — The producing team owns the data and the contract, the platform team owns the tests running and the alerting; datasets with no named owner are the ones that rot.
- What goes into a data quality SLA? — Freshness target, expected volume range, the definition of complete, the owner and escalation path, and the consequence when it is breached.
- ★ How do you fix a timezone bug at a date boundary? — Store UTC plus the source offset, define the business date once in the model layer, and test the boundary-hour count against the source.
- What would you check first if a report's numbers look wrong? — Freshness and volume of the underlying table, then recent deploys and schema changes, then reconcile the metric against the source at the same grain.

## Traps
- Answering "how do you ensure quality" with tool names — the interviewer wants the dimensions, the specific test per layer, and what happens when a test fails.
- Testing uniqueness on the surrogate key — it is generated, so it is always unique; the duplicate lives on the business key.
- Assuming the warehouse enforces your PK/FK — Redshift, Snowflake and BigQuery accept constraints as metadata and do not enforce them, so duplicates and orphans arrive silently.
- Treating a green DAG as a quality signal — success means the code ran, not that the numbers are right.
- Blocking everything, or blocking nothing — one global policy is always wrong; tier the datasets, fail fast on financial totals, quarantine on optional fields.
- Reconciling against a source read taken after the extract — the source has moved on, so the counts can never tie; reconcile as of the extract watermark.

## Graph
- **Needs first:** [[pipeline-design]]
- **Leads to:** [[data-governance]], [[observability]]
- **Asked together with:** [[dbt-transformations]]
