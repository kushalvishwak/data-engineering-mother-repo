# Spark interview practice

## Explain a shuffle and why it matters.

**Short answer:** a shuffle redistributes records across partitions so downstream operations can group, join, or sort them by key.

**Deep explanation:** it introduces network transfer, serialization, disk spill, and stage boundaries. Partition sizing and key skew affect task duration. Spark's logical optimizer (Catalyst) plans transformations; physical operators execute them, while Tungsten-related execution optimizations improve memory/CPU use. Inspect the plan and Spark UI rather than inferring from source code.

**Example:** `groupBy(key).agg(...)` usually requires records for each key to meet in a partition.

**Common mistake:** assuming every transformation causes a shuffle or that more partitions always fix a slow job.

**Senior follow-up:** when can AQE help? It can adapt portions of a plan from runtime statistics, such as coalescing partitions or handling skew, subject to Spark version and configuration.

## `repartition` vs `coalesce`?

**Short answer:** repartition redistributes data with a shuffle; coalesce can reduce partitions with less movement but may create uneven work.

**Deep explanation:** use repartition when balancing data or changing partitioning is worth the exchange. Use coalesce to reduce output task count when the current distribution remains acceptable. Neither replaces measuring task sizes or file output.

**Example:** after filtering most rows, coalesce may reduce tiny output files; repartition by a write key can distribute data but incurs a shuffle.

**Common mistake:** using coalesce to solve skew or repartitioning to one partition for large output.

**Senior follow-up:** how do you tune file sizes? Measure output file distribution, parallelism, downstream pruning, and compaction cost.
