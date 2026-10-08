---
id: dbt-transformations
title: dbt Transformations
tier: 1
priority: should-know
sources: [obenner/dbt, obenner/dwha, obenner/data-quality, devinterview, cookbook]
---

# dbt Transformations

## Say it in one line
dbt is the T in ELT: you write `SELECT` statements, and dbt turns them into a dependency-ordered DAG of tables and views inside your warehouse, with tests, documentation and lineage attached.

## Must be able to recite
- **Model** — One `.sql` file containing a single `SELECT`; dbt wraps it in the DDL needed to build a relation in the warehouse.
- **`ref()`** — Declares a dependency on another model, which is how dbt builds the DAG, orders execution and resolves the right database/schema per environment.
- **`source()`** — Declares a raw upstream table described in YAML, giving freshness tests and lineage that reaches back to the true origin.
- **Materialisations** — `view`, `table`, `incremental`, `ephemeral` (inlined as a CTE, no object created), plus `materialized_view` and `snapshot`.
- **Incremental model** — Processes only new or changed rows, guarded by `{% if is_incremental() %}` and a `unique_key`; `--full-refresh` rebuilds it from scratch.
- **Incremental strategies** — `append` (insert only), `merge` (upsert on `unique_key`), `delete+insert`, `insert_overwrite` (replace whole partitions), and `microbatch` (one batch per time slice, dbt 1.9+).
- **Snapshots** — dbt's SCD2: it adds `dbt_valid_from`, `dbt_valid_to` and `dbt_scd_id`, and inserts a new version row whenever a tracked column changes.
- **Snapshot strategies** — `timestamp` trusts an `updated_at` column, `check` compares a listed set of columns; timestamp is cheaper and preferred when the column is trustworthy.
- **Generic vs singular tests** — Generic tests (`unique`, `not_null`, `accepted_values`, `relationships`, or custom) are attached in YAML; a singular test is a SQL file that must return zero rows.
- **Source freshness** — `dbt source freshness` warns or errors when the newest row is older than a threshold, catching broken ingestion before the marts do.
- **Macros** — Jinja functions that generate SQL, used to remove repetition and standardise logic; overuse makes the compiled SQL unreadable and undebuggable.
- **Layers** — staging (rename and cast, close to source), intermediate (reusable joins and logic), marts (facts, dimensions and metrics-ready tables).
- **Exposures** — YAML declarations of downstream consumers such as a dashboard or ML job, so lineage and selection extend past the warehouse boundary.
- **Lineage and docs** — `dbt docs generate` derives a browsable DAG entirely from `ref()` and `source()`; the graph is never hand-maintained.
- **Slim CI (`state:modified+`)** — Compares against a stored manifest and builds only changed models plus their children, so CI does not rebuild the whole project.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ What is an incremental model and what problem does it solve? — It processes only new or changed rows instead of rebuilding the table, cutting runtime and cost on large datasets, at the price of needing correct keys and a rule for updates.
- ★ How do you design a reliable `unique_key` for an incremental model? — Use a stable business key or a surrogate key built from stable columns, and pair it with a deterministic "latest wins" rule such as `updated_at` so merges are correct.
- ★ What are snapshots and when do you use them? — They capture history from a mutable source by writing a new row when a tracked column changes, which is how you get SCD2 and point-in-time analysis without changing the source.
- ★ What tests would you put on a critical mart table? — Primary-key `unique` and `not_null`, `not_null` on the measures the business reads, `relationships` to the parent dimensions, `accepted_values` on status codes, plus a freshness check on the sources feeding it.
- ★ How do you handle a late-arriving update in an incremental model? — Widen the incremental filter to a lookback window rather than the exact watermark, and use `merge` on the `unique_key` so a re-seen row updates in place instead of duplicating.
- What is dbt and where does it sit in the stack? — A transformation framework where SQL and Jinja-templated SQL become a DAG of models that dbt runs in dependency order, with tests and documentation, against a warehouse or lakehouse.
- How is dbt different from Airflow? — Airflow orchestrates tasks of any type on a schedule; dbt only handles SQL transformations and their dependency graph, and is typically invoked as one Airflow task.
- What does `ref()` do and why does it matter? — It creates the dependency edge dbt uses to order execution and to rewrite the relation name for the current environment, and it is what makes automated lineage possible.
- What is a materialisation, and when would you choose view over table? — Materialisation is how dbt builds the model; views cost nothing to store and always reflect upstream, tables cost storage and a refresh but pay off when many expensive queries reuse the result.
- What are the typical layers in a dbt project? — Staging for light cleaning and renaming, intermediate for reusable transformations and joins, marts for business-facing facts, dimensions and metrics.
- What are sources and how do you test them? — Sources declare upstream tables in YAML; you attach freshness thresholds and column tests so broken ingestion or schema drift is caught at the boundary.
- What are macros and when should you use them? — Jinja functions that emit SQL, used for repeated patterns, standard column selection and dynamic filters; keep genuine business logic in models where it is reviewable.
- What is state selection / slim CI and why does it help? — It builds only the models that changed against a previous manifest plus their dependents, so pull-request CI validates the affected subgraph without a full rebuild.
- How do you set up CI/CD for a dbt project? — In CI run `dbt deps`, `dbt compile`, then the selected models and tests; in CD deploy artefacts and run the scheduled production job, with code review and tests required for critical marts.
- How does dbt know the order to build models in? — Purely from `ref()` and `source()` calls, which form the DAG; there is no manual dependency list to maintain.
- What happens if you hard-code a table name instead of using `ref()`? — dbt loses the dependency edge, so the model can build before its parent and the lineage graph is wrong, and it will point at the wrong environment.
- Where does the transformation actually run — in dbt or in the warehouse? — In the warehouse; dbt only compiles and dispatches SQL, so performance and cost tuning is warehouse tuning.
- How would you implement SCD2 without snapshots? — Compare the incoming batch against the current rows, close the changed ones by setting `valid_to` and `is_current = false`, then insert the new versions in the same transaction.
- What does `dbt build` do that `dbt run` does not? — `build` runs models, tests, seeds and snapshots in DAG order and stops a subtree when its test fails, whereas `run` only materialises models (not in sources, but standard).
- What is an ephemeral model and what is a seed for? — Ephemeral models are inlined as CTEs and create no object, useful for small shared logic; seeds are small CSV reference files version-controlled and loaded as tables (not in sources, but standard).
- A source added a column and your incremental model ignored it — why? — An incremental table keeps its existing shape, so you must set `on_schema_change` or run `--full-refresh` for the new column to appear (not in sources, but standard).
- How far does dbt lineage extend, and how do you show a dashboard depends on a model? — `ref()`/`source()` give lineage inside the project, and an exposure declares the downstream dashboard or job so it appears in the graph and in selection.

## Traps
- Calling dbt an ETL tool; it has no extract or load, so something else must land the raw data first.
- Claiming incremental is always faster: a wrong `unique_key` duplicates silently, and a `merge` against a huge unpartitioned target can cost more than a full rebuild.
- Snapshotting a source that hard-deletes rows — a deleted row simply stops changing, so it stays flagged current unless you configure delete handling.
- Hard-coding schema names or raw table names instead of `ref()`/`source()`, which breaks both the DAG and dev/prod separation.
- Hiding business rules inside layers of macros until nobody can read the compiled SQL; macros exist to remove repetition, not to hide logic.
- Running tests only after the whole project builds; use `dbt build` so a failing test stops its dependents instead of publishing bad marts.

## Graph
- **Needs first:** [[etl-vs-elt]], [[dimensional-modeling]]
- **Leads to:** [[data-quality]]
- **Asked together with:** [[warehouse-engines]]
