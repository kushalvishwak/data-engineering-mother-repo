# Scenario-based interview practice

## A pipeline succeeded, but the output count is 40% below normal. What do you do?

**Short answer:** stop downstream promotion, establish scope, compare independent evidence, and recover from a known-good input boundary.

**Deep explanation:** verify source completeness/manifest, schema or filter changes, partition coverage, and recent deployments. Preserve run metadata and avoid rerunning blindly into a non-idempotent sink. Notify product owners with impact and next update; validate corrected output against controls before republishing.

**Example:** compare source file counts and partition totals against prior periods; isolate a missing source partition; replay it into staging and reconcile before atomic promotion.

**Common mistake:** treating scheduler success as proof of data completeness or patching production output manually without lineage.

**Senior follow-up:** what prevention work follows? Add completeness contracts, trend alerts, deployment tests, replay automation, and ownership/runbook updates.

## A Spark job has one task running 20x longer than the rest.

**Short answer:** inspect key distribution, shuffle partition metrics, spills, and the physical plan to determine skew or straggler cause.

**Deep explanation:** compare task input and shuffle bytes, records, GC, spill, executor health, and locality. If one key dominates, use pre-aggregation, skew handling, or targeted salting; if executor-specific, investigate resource health. Re-run on representative data and check correctness.

**Example:** split a known hot key into salted subkeys for partial aggregation, then combine results, while ordinary keys retain their direct path.

**Common mistake:** blindly raising executor count or partition count without identifying the bottleneck.

**Senior follow-up:** how do you prevent recurrence? Track skew metrics and input distribution trends, set representative performance tests, and document thresholds for intervention.
