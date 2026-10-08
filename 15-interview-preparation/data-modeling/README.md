# Data modeling interview practice

## Explain the grain of a fact table.

**Short answer:** grain states exactly what one row represents, before measures or keys are selected.

**Deep explanation:** grain controls valid joins, uniqueness tests, aggregation, and interpretation. A declared business key may differ from a physical surrogate key. Facts at different grains should not be mixed without explicit allocation or aggregation.

**Example:** one row per order line per source version differs from one row per order; line revenue can be safely summed while order-level shipping may be duplicated by a line join.

**Common mistake:** defining grain as a list of columns without stating the real-world event represented.

**Senior follow-up:** how do late corrections change a dimensional model? Decide whether the fact is overwritten, versioned, or represented as an adjustment; preserve auditable semantics.

## When do you use SCD Type 2?

**Short answer:** when analysts need to associate facts with the dimension attributes valid at the fact's business time.

**Deep explanation:** Type 2 creates effective-dated versions and requires interval invariants, stable change ordering, and late-arrival policy. Type 1 is preferable when past values should be restated. Some attributes may use different policies.

**Example:** preserve customer segment history for historical revenue reporting, while correcting a misspelled display name as Type 1.

**Common mistake:** applying Type 2 to every column or using load timestamp as valid time without justification.

**Senior follow-up:** how do you model a late change? Recompute affected validity intervals and assess whether fact foreign keys need restatement.
