# 16 · Data engineering design patterns

Patterns are trade-offs, not prescriptions. This module covers landing/quarantine/curated zones, medallion layering, outbox and CDC ingestion, idempotent upsert, schema registry/contracts, replayable event logs, and immutable run manifests.

For each pattern record the problem, invariants, failure cases, operational burden, and alternatives. Medallion layers are logical quality boundaries; they do not require a particular number of physical copies or a vendor-specific product.

Exercise: choose between full snapshot, timestamp watermark, and log-based CDC for a mutable source. Compare deletes, late updates, source load, replay, and operational complexity.
