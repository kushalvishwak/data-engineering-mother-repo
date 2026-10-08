# PySpark interview practice

## How do you handle skewed joins?

**Short answer:** inspect task-level metrics and key distribution first, then select a targeted strategy.

**Deep explanation:** AQE may split skewed partitions depending on Spark version/settings. Other options include pre-aggregation, broadcasting a safely small side, salting hot keys, or isolating exceptional keys. Each changes memory, shuffle, or semantic complexity. Verify output equality and plan changes.

**Example:** aggregate events by key before joining when the downstream question only needs per-key totals.

**Common mistake:** increasing shuffle partitions globally without diagnosing a single dominant key.

**Senior follow-up:** what evidence justifies broadcast? Build-side size under realistic compressed/in-memory expansion, executor memory headroom, and the physical plan showing the intended join.

## When should you cache a DataFrame?

**Short answer:** when an expensive deterministic result is reused enough to offset cache materialization and memory pressure.

**Deep explanation:** Spark is lazy; cache is populated when an action runs, may evict blocks, and competes with execution memory. Cache narrow, reused intermediates where possible; unpersist promptly. Compare recomputation and spill metrics.

**Example:** a cleaned dimension used by several downstream actions in the same application may benefit if it fits safely.

**Common mistake:** caching every intermediate or expecting cache to make the first action faster.

**Senior follow-up:** how do you validate the result? Compare runtime, storage memory, recomputation, spill, and executor stability across representative runs.
