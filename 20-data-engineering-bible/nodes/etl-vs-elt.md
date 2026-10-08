---
id: etl-vs-elt
title: ETL vs ELT
tier: 1
priority: must-know
sources: [obenner/dwha, obenner/dbt, obenner/system-design, devinterview, cookbook]
---

# ETL vs ELT

## Say it in one line
ETL transforms data in a separate engine before it lands, ELT lands raw data in the warehouse first and transforms it there with the warehouse's own compute.

## Must be able to recite
- **ETL** — Extract, transform in a dedicated engine, then load finished tables; the target only ever sees modelled data.
- **ELT** — Extract, load raw into the warehouse, then transform in SQL inside it; raw stays queryable and re-runnable.
- **Why ELT won** — Cloud warehouses separated storage from compute and made both cheap and elastic, so the transform no longer needs its own server farm.
- **Staging area** — Transient landing zone where data is extracted, cleaned, restructured and given surrogate keys before the target load.
- **Full load** — Truncate the target and reload everything; no change-detection logic, but the cost grows with the whole table.
- **Incremental (refresh) load** — Apply only rows new or changed since the last run; cheap, but needs a reliable watermark and a dedup rule.
- **Bronze / silver / gold** — Immutable raw, cleaned and deduplicated, then business-ready marts; the layering is what makes reprocessing safe.
- **Who does what** — Ingestion tools (Sqoop, Fivetran, ADF, Glue, Debezium) do the EL, dbt or SQL does the T, an orchestrator sequences them.
- **Schema-on-write vs schema-on-read** — ETL fixes the schema at load time, ELT defers it and trades load-time safety for flexibility.
- **Lineage** — The recorded path of a column from origin through transformations to destination; mandatory for audit in banks and for impact analysis.
- **ETL-t** — Standard ETL with a dedicated data-quality and testing pipeline bolted on after the load.
- **Tools actually named in Indian enterprise interviews** — Informatica PowerCenter, IBM DataStage, SSIS, Talend, Azure Data Factory, AWS Glue.
- **When ETL is still correct** — PII must be masked or tokenised before it lands, or the target cannot transform (licence-limited or legacy MPP).
- **Reverse ETL** — Pushing modelled warehouse tables back out into operational SaaS systems; the transform is already done.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ What is the difference between ETL and ELT, and why has ELT become the default? — ETL transforms before loading, ELT loads raw then transforms in the warehouse; ELT won because warehouse compute is elastic, so keeping raw data and re-deriving marts is cheaper than a separate transform tier.
- ★ Explain the ETL process and its stages. — Extract from sources, transform (clean, type-cast, deduplicate, enrich, apply business rules), load into the target with `INSERT`/`MERGE`.
- ★ What is the difference between full load and incremental (refresh) load? — Full load erases and reloads the target each run; incremental load applies only changes since the last run, which is faster but needs change detection and consistency handling.
- ★ What is a staging area and why is it important? — A temporary area between source and target where you validate, clean, restructure and assign surrogate keys, so the target is never the place you discover bad data.
- ★ How do you model raw/bronze, silver and gold layers? — Bronze is immutable ingested data, silver is cleaned/standardised/deduplicated with stable schemas, gold is business-facing marts and aggregates.
- What are the common challenges in an ETL process? — Data quality, scalability with volume, real-time expectations against batch design, governance and GDPR, time-zone and timestamp inconsistencies, legacy sources, metadata and lineage.
- What is an ETL pipeline? — A scheduled, dependency-ordered set of steps that lands source data in an analytics target in a repeatable, monitorable way.
- What ETL tools exist and how do you choose? — Informatica, DataStage, SSIS, Talend, Glue and ADF for graphical enterprise ETL; SQL/dbt plus an orchestrator for ELT; choose by where the compute and the skills already are.
- What is the difference between an ETL tool and an OLAP tool? — ETL tools move and reshape data into the warehouse; OLAP tools query and aggregate what is already there for analysis.
- Compare ETL-tool development with hand-coded development. — Tools give visible logic, metadata, error handling and load logs cheaply; hand-coded pipelines are more flexible but degrade in maintainability as volume and staff turnover grow.
- What are the different methods of loading dimension tables? — Conventional load checks all table constraints as rows arrive; direct load disables constraints for speed and validates afterwards, isolating the rows that fail.
- How do you load a time/date dimension? — Generate it once with a program that loops over every date in the required range, one row per day, rather than deriving it from transactional data.
- ★ What is data lineage and why do interviewers care? — It is the recorded origin, transformation and destination of data; without it you cannot answer "where did this number come from", which is the first question in any bank audit.
- How do you move data from the ingest layer to the consumption layer in a serverless setup? — Land raw into object storage, trigger transformation on arrival or on schedule, and publish curated tables to the query engine, with each hop idempotent.
- What is real-time data warehousing? — The warehouse captures business activity as it completes rather than on a nightly cycle, so the activity is queryable almost immediately.
- What are staging, intermediate and mart layers in a transformation project? — Staging is light renaming and casting close to the source, intermediate holds reusable joins and logic, marts hold the fact and dimension tables the business queries.
- What is a lookup table in an ETL flow? — A reference table matched on the target's key to decide whether a row is new or changed, so only modified records are applied.
- What is an aggregate table and why build one? — A pre-summarised table at a coarser grain than the fact table; it cuts query cost and time at the price of extra storage and a refresh dependency.
- How do you validate a data mart after a load? — Reconcile row counts and control totals against the source, re-run key business measures, and check referential integrity before releasing the load to users.
- How do you handle semi-structured and unstructured sources in an ETL design? — Land them raw as files or JSON, parse and flatten in a transformation step, and keep the raw copy so a parsing bug can be fixed by reprocessing.
- How do you monitor an ETL process? — Track run status, duration, row counts in and out, freshness of the target, and failed-record counts, with alerting tied to the load SLA.
- Where do you mask or tokenise PII — before or after the load? — Before, if policy forbids raw PII landing in the analytics platform; that requirement alone can force ETL over ELT (not in sources, but standard).

## Traps
- Answering "ELT is always better" without the conditions: ELT assumes warehouse compute is your cheapest compute and that raw sensitive data is allowed to land.
- Confusing the staging area (transient, per-run, thrown away) with the raw/bronze layer (permanent, immutable, the thing you replay from).
- Describing incremental load as just `WHERE updated_at > last_run`: that misses hard deletes and any row updated inside the same timestamp granularity.
- Using ETL and ELT as labels for tools rather than for where the transform runs — dbt only does the T, and it pushes that T down into the warehouse.
- Forgetting to say what happens on re-run; a load design with no idempotency story is the fastest way to fail this question.

## Graph
- **Needs first:** [[warehouse-architecture]]
- **Leads to:** [[pipeline-design]], [[dbt-transformations]]
- **Asked together with:** [[cloud-fundamentals]]
