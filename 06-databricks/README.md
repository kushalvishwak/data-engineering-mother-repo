# 06 · Databricks and Delta Lake

Treat Databricks features as platform capabilities layered on Spark and Delta Lake; check runtime/version availability. Delta transaction logs record table versions and actions; readers use a consistent snapshot while commits coordinate changes.

Study transaction semantics, schema enforcement/evolution, `MERGE`, Change Data Feed, retention/VACUUM safety, OPTIMIZE, data skipping, Z-Ordering, and Liquid Clustering. Z-Ordering co-locates related values in files; Liquid Clustering is a distinct managed clustering approach. Avoid applying both as interchangeable magic settings. Benchmark representative filters and write patterns.

Auto Loader incrementally discovers files and tracks ingestion state; design schema evolution and checkpoint recovery deliberately. Unity Catalog centralizes governed access and metadata; use least privilege, ownership, lineage, and auditable grants. Exercise: design a replay-safe bronze-to-silver flow with CDF and schema drift handling.

Before a maintenance operation, capture the table/runtime context, retention and recovery requirements, active readers/writers, and the expected file/scan metrics. See [`docs/delta-operation-checklist.md`](docs/delta-operation-checklist.md); exact command behavior and feature availability must be checked against the deployed Databricks Runtime and product documentation.
