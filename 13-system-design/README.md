# 13 · Data system design

Start from workload and service objectives: producers, consumers, volume, growth, latency, freshness, availability, retention, privacy, and recovery. Draw components and data/state boundaries; state assumptions before naming products.

For batch, consider replayable source snapshots, incremental checkpoints, atomic publication, and backfill isolation. For streaming, include partition ordering, event time, state retention, replay, and sink idempotency. For lakehouse design, cover catalog/governance, open formats, compaction, concurrency, and workload isolation.

Exercise: design a platform for 30 source systems, two-hour freshness, regulated customer data, and both BI and feature consumers. Explain failure domains, access boundaries, lineage, cost controls, and migration stages.
