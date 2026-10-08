---
id: warehouse-architecture
title: Data Warehouse Architecture
tier: 0
priority: must-know
sources: [obenner/dwha, obenner/system-design, devinterview, cookbook]
---

# Data Warehouse Architecture

## Say it in one line
A data warehouse is a subject-oriented, integrated, time-variant, non-volatile store of historical data built for analysis, and its architecture is the set of layers data passes through between the source systems and the BI tool.

## Must be able to recite
- **The four defining properties (Inmon)** — subject-oriented, integrated, time-variant, non-volatile; recite those four words, because "a big database for reporting" is the answer that fails.
- **Three-tier architecture** — bottom tier is the sources plus staging and ETL, middle tier is the warehouse and its serving/OLAP engine, top tier is the BI and analysis clients; the same path in modern naming is staging → core → marts, or bronze → silver → gold.
- **Staging area** — a transient landing zone where extracts are cleaned, restructured, conformed and assigned surrogate keys before the warehouse load; users never query it and it is usually truncated each run.
- **ODS (operational data store)** — an integrated, near-real-time, current-state copy of operational data holding little or no history, used for operational reporting and legitimately usable as the source for a data mart.
- **Core / integration layer** — the enterprise-wide conformed and historised model that is the single version of the truth: 3NF in Inmon's design, conformed dimensional in Kimball's, hubs/links/satellites in Data Vault.
- **Data mart** — a subject- or department-scoped subset (an accounts mart and a loans mart in a bank); a *dependent* mart is fed from the warehouse and stays consistent, an *independent* mart pulls straight from operational systems and drifts into a competing version of the truth.
- **Medallion (bronze/silver/gold)** — bronze is immutable raw ingestion with minimal transformation, silver is cleaned, standardised and deduplicated with stable schemas, gold is business-ready marts and aggregates; the value is reprocessability, clear contracts and governance per layer.
- **Inmon, top-down (Corporate Information Factory)** — build one normalised enterprise warehouse first, subject area by subject area, then spin dimensional marts off it; slowest to first report, strongest consistency and least rework.
- **Kimball, bottom-up (bus architecture)** — build dimensional marts one business process at a time and bind them together with conformed dimensions registered on a bus matrix, so the warehouse *is* the union of the marts; fastest delivery, and it only holds together if conformance is enforced.
- **Data Vault 2.0** — hubs hold business keys, links hold relationships, satellites hold descriptive attributes with full history; it is built for auditability, source volatility and parallel loading, and it feeds star schemas rather than replacing them.
- **Data warehouse vs data lake** — the warehouse stores modelled, curated, schema-on-write tabular data for BI; the lake stores raw files of any structure on cheap object storage, schema-on-read, for data science, replay and cheap retention. A lake without a catalogue, ownership and quality checks becomes a data swamp.
- **Lakehouse** — lake storage plus an open table format (Delta, Iceberg, Hudi) giving ACID commits, schema evolution, time travel and upserts, so one copy of the data serves both BI and ML; that is the honest answer to "are there data lake warehouses?".
- **EDW vs warehouse vs mart** — the EDW is the union of every subject area across the enterprise, a warehouse may cover one subject area or one system, a mart is one department's slice of it.
- **Virtual (federated) warehousing** — no physical consolidation; users query operational sources directly through a semantic or virtualisation layer. Always fresh and cheap to build, but it loads the OLTP systems and cannot conform or retain history.
- **Full load vs incremental load** — a full load truncates and reloads everything; an incremental load applies only the changed rows using a watermark or CDC, and it is the only affordable option once volumes grow, at the cost of needing reliable change detection and idempotent writes.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ What is a data warehouse and what are its key characteristics? — A central repository consolidating data from many sources for query and analysis rather than transaction processing: subject-oriented, integrated, time-variant, non-volatile, denormalised and dimensionally modelled, loaded by ETL/ELT.
- ★ What is the difference between a data warehouse and a data lake? — The warehouse holds modelled, cleaned, schema-on-write tabular data optimised for BI and SQL; the lake holds raw files of any format on object storage, schema-on-read, cheap to retain and suited to data science and reprocessing. Warehouse first for governed metrics, lake first for volume, variety and replay.
- ★ Are there data lake warehouses? What is a lakehouse? — Yes: a lakehouse is lake storage plus an open table format (Delta, Iceberg, Hudi) that adds ACID commits, upserts, schema evolution and time travel, so one copy of the data serves both BI and ML without a separate warehouse load.
- ★ What is a data mart, and how does it differ from a data warehouse? — A mart is one subject area or department's slice (accounts, loans, sales); the warehouse integrates many subject areas, and in practice an enterprise warehouse is the set of conformed marts plus the integration layer beneath them.
- ★ What is the main difference between the Inmon and Kimball philosophies? — Inmon builds one normalised enterprise warehouse subject area by subject area and derives marts from it (top-down); Kimball builds dimensional marts per business process and ties them together through conformed dimensions, so the warehouse is the union of the marts (bottom-up).
- ★ What is data warehouse architecture / what is a three-tier data warehouse? — Bottom tier: source systems, staging and ETL. Middle tier: the warehouse plus the OLAP/serving engine that presents usable data. Top tier: reporting, dashboards and ad-hoc analysis clients.
- ★ What is a staging area and what happens in it? — A transient area between extract and load where data is restructured, cleansed, value-transformed and given surrogate keys; keeping it separate means the warehouse never sees half-processed data and reloads can be rerun.
- ★ What is an ODS, and is it correct to build a data mart from an ODS? — An ODS is an integrated near-real-time store of current operational data with little history, used for operational reporting. Yes, a mart can be built from it, precisely because a mart often needs current detail rather than deep history.
- ★ What is a real-time data warehouse and how does it differ from near-real-time? — A real-time warehouse reflects source changes as they happen, which fights the reason warehouses were separated from operational systems (aggregates and surrogate keys must be maintained continuously). Near-real-time simply runs the pipeline more often, for example every two hours, with selective refresh of the volatile tables — that is what most "real-time" projects actually deliver.
- ★ What is metadata in a warehouse context and why does it matter? — Data about the data: source and lineage, physical type and length, valid values, and derivation rules, held in a catalogue or data dictionary. It is what lets consumers trust a column and what insulates the warehouse from source schema changes.
- What are the different types of data warehousing? — Enterprise data warehouse, operational data store and data mart; they differ by scope, history depth and latency, not by technology.
- What is the difference between an EDW and a data warehouse? — An EDW spans the whole enterprise and integrates every diversified source; a "data warehouse" may be a single subject area or single system's warehouse, and the EDW is the combination of them all.
- What are the steps to build a data warehouse? — Gather business requirements, identify sources, identify the facts, define the dimensions and their attributes, refine them, organise the attribute hierarchies, define relationships, then assign surrogate keys.
- What are the fundamental stages of data warehousing maturity? — Offline operational database (a copy on another server so reporting does not hurt the source), offline warehouse (loaded periodically into a reporting structure), real-time warehouse (updated as transactions occur), integrated warehouse (results fed back into the operational systems).
- What is virtual data warehousing? — A point-to-point strategy in which end users query the operational databases directly through the access layer, with no physical consolidation; cheap and fresh, but it loads the source systems and cannot conform history.
- What is the difference between a dependent and an independent data mart or warehouse? — Dependent structures take their data from the warehouse; independent ones read the operational sources directly, which is faster to build and the usual cause of two departments reporting different numbers.
- What is full load versus incremental (refresh) load? — Full load truncates the target and reloads everything; incremental load applies only ongoing changes on a schedule, which requires a watermark or CDC and idempotent writes but is the only workable option at scale.
- How do you model bronze/silver/gold layers? — Bronze is immutable raw ingestion with minimal transformation; silver is cleaned, standardised and deduplicated with consistent schemas; gold is business-ready marts and aggregates for BI and applications. The point is safe reprocessing and an explicit contract at each boundary.
- How would you design an end-to-end batch analytics pipeline? — Ingest into an immutable raw layer, transform into curated conformed datasets, publish marts for BI, and attach an SLA, quality checks and a named owner to every dataset; schedule hourly or daily and optimise for correctness and cost rather than latency.
- What are aggregate tables and when do you build them? — Pre-summarised copies of a fact at a coarser grain, built when the same heavy group-by runs repeatedly; they cut scan cost and server load, and the price is refresh logic plus the risk of them disagreeing with the detail.
- What is data cleaning and which problems does it fix? — Applying business rules before load to fix missing columns from one source, inconsistent values across sources, orphan records, outliers, mismatched data types for the same field, and rows that breach business rules.
- What are the data validation strategies after a mart load? — Reconcile source and target totals with SQL scripts when both are relational, use control tables or spreadsheets for flat-file sources, and check row counts, key uniqueness and known-entity samples. (The sources claim warehouse testing is manual only; that is outdated — dbt tests, Great Expectations and Soda are standard now.)
- Can you have two data lakes inside a single warehouse? — Technically yes: a warehouse can register several external storage locations as separate external schemas or catalogues. The real question is governance — two lakes means two sets of conformance rules, so you need one catalogue, one set of keys and one owner per dataset.
- What is a VLDB? — A "very large database"; the threshold moves, but roughly a terabyte and up, at which point partitioning, parallel load and archival strategy stop being optional.
- What is the difference between metadata and a data dictionary? — Metadata is the general category (everything known about the data, including lineage and process); the data dictionary is the catalogue artefact that stores the structural part of it, such as names, types, lengths and valid values.
- What are the possible data marts in retail sales? — Product/inventory and sales are the standard two; a fuller build adds store, promotion, customer loyalty and returns marts, all sharing conformed date, product and store dimensions.
- How do you design for schema evolution between layers? — Define compatibility rules, version the schema or contract, and enforce them in CI and at ingestion; downstream models should tolerate added fields but fail fast on breaking changes, and outputs that many consumers depend on stay backward compatible.
- What is Data Vault and when would you use it? — Hubs (business keys), links (relationships) and satellites (historised descriptive attributes). You use it when sources change often, when auditability and full lineage are mandatory (common in banking), and when many teams must load in parallel; you still build star schemas on top for consumption. (not in sources, but standard)
- What is a slowly changing fact? — A measure that is restated after it was first loaded (a corrected settlement amount, a rebooked transaction). You either insert a reversing row plus the corrected row so the audit trail survives, or rewrite the affected partition, which is simpler but loses the history of the correction. (not in sources, but standard)

## Traps
- Defining a warehouse as "a big database for reports" — recite the four properties; non-volatile and time-variant are the two that separate a warehouse from an ODS or a replica.
- Saying data lakes replaced warehouses — a lake with no table format, catalogue or modelling is a swamp; the current answer is the lakehouse, i.e. warehouse semantics on lake storage.
- Getting Inmon and Kimball the wrong way round — the hook is "Inmon integrates first, Kimball delivers first": Inmon is top-down and normalised, Kimball is bottom-up and dimensional.
- Treating staging and an ODS as the same layer — staging is transient, unmodelled and never queried by users; an ODS is integrated, current-state and deliberately queryable.
- Calling a 15-minute schedule real-time — say micro-batch or near-real-time and give the actual interval; bank interviewers probe this because their SLAs are written in those words.
- Naming the medallion layers without saying what changes between them — the answer is the transformation contract at each boundary (immutability, deduplication and conformance, then business rules), not the colours.

## Graph
- **Needs first:** [[dimensional-modeling]]
- **Leads to:** [[etl-vs-elt]], [[warehouse-engines]]
- **Asked together with:** [[table-formats-lakehouse]]
