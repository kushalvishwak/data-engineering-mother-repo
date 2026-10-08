# 20 · Interview projects

Use these time-boxed exercises to show reasoning and implementation judgment. Clarify assumptions, sketch the data flow, identify failure semantics, then present a small testable core. Do not spend the session naming services before stating requirements.

## Practice cases

1. **30 minutes · CDC design:** ingest mutable customer records with deletes and out-of-order updates. Define ordering, deduplication, replay, and history.
2. **45 minutes · Spark diagnosis:** a join has one slow task and spills heavily. Explain what metrics and plan you inspect before changing partitioning or join strategy.
3. **60 minutes · Lakehouse design:** design bronze/silver/gold publication with schema drift, governance, backfills, and BI consumers.
4. **45 minutes · Streaming recovery:** explain checkpoint loss, source retention, duplicate sink writes, and bounded reprocessing.
5. **60 minutes · Incident response:** freshness is met but revenue is 12% low. Identify validation, rollback, reconciliation, and communication steps.

For each case, deliver: assumptions, diagram, invariants, failure modes, security boundary, cost drivers, tests, and one alternative with its trade-off.
