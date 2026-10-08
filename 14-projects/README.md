# 14 · Progressive projects

Projects increase in scope from a local batch job to a governed enterprise platform. Use synthetic data, make design assumptions explicit, and add operational complexity only when a project needs it. Cloud deployment stays optional unless explicitly required.

| # | Project | New engineering challenge | Completion evidence |
|---:|---|---|---|
| 01 | [Basic batch pipeline](01-basic-batch-pipeline/README.md) | Parse/validate, quarantine, aggregate, and atomically publish | Run the standard-library pipeline and tests; reconcile accepted and rejected row counts |
| 02 | [API ingestion pipeline](02-api-ingestion-pipeline/README.md) | Pagination, rate limits, durable raw pages, and replay | Fake-transport tests plus a documented archive-before-checkpoint boundary |
| 03 | [Medallion lakehouse](03-medallion-lakehouse/README.md) | Bronze/silver/gold quality boundaries, schema drift, governance | Table contracts, representative plan, quality gate, and publication decision |
| 04 | [Incremental data pipeline](04-incremental-data-pipeline/README.md) | Watermarks, deletes, late data, and state recovery | Prove reruns, backfills, and partial failure do not skip or double-apply data |
| 05 | [SCD Type 2 pipeline](05-scd-type-2-pipeline/README.md) | Effective intervals, source ordering, and replay-safe history | Assert one current row and non-overlapping half-open intervals |
| 06 | [Streaming pipeline](06-streaming-pipeline/README.md) | Event time, watermarks, checkpoint recovery, and sink semantics | Replay duplicate/late events and state a precise delivery guarantee |
| 07 | [Real-time data platform](07-real-time-data-platform/README.md) | Service boundaries, latency objectives, and operating model | Architecture, SLOs, failure-domain analysis, and cost model |
| 08 | [Enterprise lakehouse](08-enterprise-lakehouse/README.md) | Domain governance, identity, lineage, and workload isolation | Access matrix, ownership model, audit path, and deployment controls |
| 09 | [End-to-end data platform](09-end-to-end-data-platform/README.md) | Integrate source onboarding, platform operations, and BI/ML consumers | Delivery plan, acceptance tests, rollback/recovery evidence, and architecture review |

## Shared project review

Every project brief includes architecture and flow, choices/trade-offs, failure scenarios, monitoring, testing, security, and cost considerations. Treat the brief as a design and acceptance contract, not a claim that a full cloud deployment already exists. The local code available today is project 01 plus focused API pagination, SCD Type 2, and data-contract examples under their topic areas; service-dependent projects remain explicit implementation briefs.

For each implementation, add an architecture diagram, config contract, synthetic fixtures, focused tests, and a runbook. Never check in cloud credentials or run a billable/destructive operation without approval and a reviewed rollback plan.
