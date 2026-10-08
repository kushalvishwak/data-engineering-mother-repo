# 12 · Data quality and contracts

Make quality executable and owned. A data contract states schema, semantics, compatibility rules, freshness, allowed nulls/ranges, privacy classification, and change process.

Use layered checks: structural (schema, parseability), row-level (domain/range), relational (uniqueness/referential integrity), and operational (volume/freshness). Decide which failures block publication, quarantine rows, or warn. Track check outcomes with dataset, partition, version, and run identity; avoid logging sensitive row content.

Exercise: write a contract for an orders fact, including uniqueness grain, currency, cancellation, allowed lateness, and breaking-change policy. Add a reconciliation that compares source manifest counts with accepted plus quarantined rows.
