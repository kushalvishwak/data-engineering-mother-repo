# Enterprise data platform design review

Design for 30 source systems, a two-hour freshness target, regulated customer data, BI and feature consumers, and daily historical corrections. State assumptions instead of treating unspecified values as facts.

## Required artifacts

- A source-to-consumer data-flow diagram with trust boundaries, control plane, and data plane.
- Workload/SLO table: volume and growth, freshness, availability, retention, RPO/RTO, concurrency, and query patterns.
- Ingestion decision per source: snapshot, cursor/watermark, CDC, or event stream, including delete and replay semantics.
- Data product ownership, contracts, schema compatibility, catalog/lineage, and consumer access model.
- Batch and streaming recovery paths, idempotency boundary, checkpoint/commit state, and backfill isolation.
- Security controls for identity, secrets, network, encryption, audit, sensitive columns, and retention.
- Observability and cost attribution: freshness/correctness SLOs, lineage, run metadata, chargeback/showback, and actionable alerts.
- Two alternatives, their trade-offs, migration stages, and the design decisions you would revisit first.

## Review rubric

Score each area from 0 (missing) to 2 (specific and defensible): requirements, correctness, failure recovery, security, governance, operational ownership, cost, and communication. A high score requires explaining the conditions under which the design changes; service-name recall alone earns no credit.
