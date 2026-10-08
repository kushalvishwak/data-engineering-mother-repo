# 05 · Apache Spark

Understand Spark's driver/executor model, jobs, stages, tasks, shuffles, and lazy evaluation before tuning configuration. Catalyst analyzes and optimizes logical plans; physical planning chooses operators. Tungsten describes execution and memory optimizations; it is not a user-facing switch.

## Performance investigation order

1. Inspect the physical plan and Spark UI: stages, shuffle bytes, spills, skew, and task duration.
2. Reduce data early with projection and selective filters; verify predicate pushdown actually occurs.
3. Choose join strategy from measured table sizes. Broadcast only when the build side safely fits executor memory.
4. Address skew with AQE, salting, pre-aggregation, or skew-aware partitioning as evidence supports.
5. Tune partition count based on task size and parallelism; `repartition` shuffles, while `coalesce` can reduce partitions with less movement but may concentrate work.

Cache only reused, expensive intermediates and unpersist when done. AQE can adapt plans using runtime statistics; its exact behavior depends on Spark version and settings. Exercise: compare plans and task metrics for a skewed join before and after a measured fix.

See [`examples/plan_inspection.py`](examples/plan_inspection.py) for a small PySpark-runtime-dependent plan-inspection scaffold. Record Spark version, configuration, input size/distribution, physical plan, and Spark UI metrics with any performance claim; a code snippet alone is not a benchmark.
