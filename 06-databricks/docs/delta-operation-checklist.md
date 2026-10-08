# Delta Lake operation checklist

Use this as a review prompt, not a version-independent command recipe.

## Before changing a table

- Record catalog/schema/table identity, runtime version, table protocol/features, current schema, and relevant table properties.
- Confirm the expected write pattern, concurrent writers, readers, and downstream consumers.
- Define a recovery point and validate that source data or a tested backup can reconstruct the intended state.
- For schema evolution, review the proposed schema diff and compatibility with readers before enabling automatic behavior.
- For `MERGE`, define source uniqueness, match key, delete semantics, retry identity, and behavior for late/out-of-order updates.

## Layout and maintenance

- Inspect file-size distribution, partition count, query predicates, and data-skipping effectiveness before compaction.
- Consider partitioning only where workload and cardinality justify it; avoid high-cardinality directory partitioning by default.
- Compare OPTIMIZE, Z-Ordering, and Liquid Clustering as workload-specific approaches, not synonymous settings. Confirm feature support and maintenance semantics for the runtime.
- Treat retention/VACUUM changes as recovery and compliance decisions. Check time-travel, streaming readers, concurrent operations, and legal retention before deleting files.
- If consuming Change Data Feed, establish consumer offsets, retention/staleness behavior, replay procedure, and schema-change handling.

## Validate and observe

Capture before/after input and output counts, file counts/size distribution, bytes scanned, task/shuffle metrics, latency, and cost. Verify logical results and history, not just command completion. Never use a production table for an exercise without explicit owner approval and a reviewed rollback plan.
