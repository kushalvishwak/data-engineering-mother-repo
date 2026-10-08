# Roadmap

This is a staged curriculum and implementation backlog, not a claim that every vendor service has a local emulator or that every proposed deployment is production-ready. Completed examples are runnable locally; service-specific work remains explicitly opt-in.

## Curriculum and implementation

- [x] Establish the 20-topic learning path and nine-project progression.
- [x] Map the 20 repositories from the supplied PDF to original curriculum areas without importing their contents.
- [x] Provide a deterministic, tested standard-library batch pipeline.
- [x] Provide local tested examples for bounded API pagination, SCD Type 2 changes, and row-level contract checks.
- [ ] Expand Python packaging, profiling, concurrency, and durable cursor examples.
- [ ] Add SQL labs for query-plan reading, transaction isolation, incremental deletes, and dialect differences.
- [ ] Add dimensional-model exercises for late-arriving facts, inferred members, and restatement.
- [ ] Add generated-data Spark labs that compare plans and measure skew, shuffle, cache, and AQE behavior.

## Platform depth

- [ ] Add isolated, opt-in Databricks notebooks for Delta transaction history, CDF, Auto Loader, and Unity Catalog.
- [ ] Add reviewed Azure and AWS deployment examples with least-privilege identities, network boundaries, and cost estimates.
- [ ] Add Snowflake labs for pruning, streams/tasks, role design, and warehouse sizing.
- [ ] Add orchestration adapters showing retry classification, backfills, concurrency limits, and idempotent task contracts.
- [ ] Add architecture options for Tableau and Power BI serving, semantic models, and workload isolation.

## Reliability, security, and architecture

- [ ] Add failure injection and measured recovery drills to all project briefs.
- [ ] Add reusable run metadata, lineage, alert routing, and SLO examples.
- [ ] Add data-contract compatibility checks and schema migration exercises.
- [ ] Add architecture decision records comparing batch, CDC, streaming, and lakehouse alternatives.
- [ ] Add threat-model and privacy-review checklists to deployment-oriented projects.

## Delivery and maintenance

- [x] Add CI for the dependency-free Python examples and tests.
- [ ] Add focused lint/type checks when their configuration and dependencies are adopted.
- [ ] Complete project implementations incrementally; retain clear scope and runtime labels.
- [ ] Add scoring rubrics and sample solution outlines to senior interview cases.
- [ ] Review vendor claims, external links, runtimes, and license notices on a documented cadence.

Vendor behavior and editions change. For service-specific expansions, record the product, feature, runtime/version, source documentation, and review date; never infer production guarantees from a local simulation.
