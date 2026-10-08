# Build log — 4 September 2026

Built in a single Claude Code session, in one sitting, from three public question banks. The
vault was created as its own directory so it shares nothing with the session's original working
tree. This log exists so the build reasoning lives with the artefact rather than in a chat
history.

## Sources

| Source | Advertised | Actually usable |
|---|---|---|
| OBenner/data-engineering-interview-questions | 38 topic files | ~2,600 questions. `sql.md` 466, `dwha.md` 283, `spark.md` 243, `data-structure.md` 222, `hadoop.md` 207. `full.md` skipped (duplicate concatenation); `delta.md`, `dynamodb.md`, `parquet.md` are 92-byte stubs. |
| Devinterview-io/data-engineer-interview-questions | "Top 100" | **15.** The repo README publishes 15 with long answers; the other 85 are paywalled on devinterview.io. All 15 are modelling/warehouse/ETL. Titles 1–69 recovered from the site into `_sources/devinterview_titles.md` and mapped to nodes; 70–100 unretrievable. |
| andkret/Cookbook §08 | question list | ~134 questions, topic-grouped, mostly unanswered. Its "Snowflake", "AWS", "GCP", "Azure", "Docker and Kubernetes" headings are empty table-of-contents stubs. |

All mirrored into `_sources/` so the vault works offline and answers stay traceable.

## Method

1. Downloaded every source locally (1.4 MB) rather than fetching per-agent.
2. Designed the taxonomy and the edge table by hand — 48 nodes across 5 tiers, with
   needs-first / leads-to / asked-together-with for each. This is the part that makes it a graph
   rather than a folder of notes, and it was deliberately not delegated.
3. Wrote `_SPEC.md` as the build contract: canonical ids, edge table, file template, seven rules.
4. Fanned out **nine subagents** in parallel, each owning a slice, each instructed to index large
   files with `grep -n '^## '` and `sed` only the ranges needed — never to read a 200 KB file whole.

| Agent | Nodes |
|---|---|
| SQL core | sql-semantics, sql-joins-sets, sql-aggregation, sql-window-functions |
| SQL DDL and patterns | sql-ctes-subqueries, sql-ddl-dml-transactions, sql-performance-indexing, sql-query-patterns |
| Modelling and warehouse | relational-modeling, dimensional-modeling, scd-history, warehouse-architecture, oltp-vs-olap |
| Pipelines and streaming | etl-vs-elt, pipeline-design, orchestration-airflow, dbt-transformations, cdc-ingestion, batch-vs-streaming, kafka-messaging, lambda-kappa |
| Spark and Hadoop | spark-core, spark-tuning, hadoop-hdfs, mapreduce, hive-impala |
| Storage and NoSQL | file-formats, table-formats-lakehouse, partitioning-layout, distributed-systems, nosql-stores |
| Cloud and engines | cloud-fundamentals, aws-data-stack, gcp-bigquery, azure-data-stack, warehouse-engines, containers-kubernetes, cost-optimization |
| Ops and scenarios | data-quality, data-governance, observability, system-design-scenarios, behavioral-project-story |
| Adjacent skills | python-for-data, dsa-coding, bi-visualization, linux-shell, apis-rest |

5. Validated centrally: five-section structure, frontmatter completeness, wikilink resolution,
   orphan detection. Commands are in `CLAUDE.md`.

## Result

48 nodes · 1,302 questions with answers · 606 ★ · 720 recite bullets · 287 traps · 608 KB.
Structure valid, zero dangling links, zero orphans.

## Defects found and fixed during the build

- `linux-shell` was an **orphan** — the edge table let it point outward but nothing pointed back.
  Fixed by making it a prerequisite of `containers-kubernetes` and a companion of
  `python-for-data`, in both nodes and in the spec table.
- Two stray 0-byte files at the repo root left by agents' shell redirections, one of which
  duplicated a node basename and would have made `[[sql-ddl-dml-transactions]]` ambiguous in
  Obsidian. Removed.
- README initially repeated the "100 questions" claim from the Devinterview title. Corrected to
  the real count once the file was inspected.

## Source rot corrected inline, not copied

These matter: answering an interview from the uncorrected banks would sound five to fifteen years
stale. Each is flagged in parentheses at the point it appears.

**Hadoop / Hive / Spark** — HDFS default block 64 MB → 128 MB; a 25 MB file described as consuming
a whole block of disk; NameNode as an unqualified single point of failure (HA with QJM exists);
client↔NameNode traffic described as SSH (it is Hadoop RPC); JobTracker/TaskTracker and ports
50070/50030 as current; Hive "always converts to MapReduce" (Tez/LLAP by default since Hive 2);
Hive "cannot update or delete" (ACID ORC since 0.14); Hive indexes (removed in Hive 3); Datasets
giving run-time rather than compile-time type safety; Mesos as a live cluster manager;
`spark.cleaner.ttl` (removed); and a source recommending a join OOM be fixed by swapping
RIGHT OUTER for LEFT OUTER.

**SQL** — Greenplum's claim that DISTINCT and GROUP BY are window functions; `SQL_CALC_FOUND_ROWS`
(deprecated in MySQL 8.0.17); `MOD(id,2)` and `WHERE id = n` row-position tricks that assume
gapless ids; `ROW_NUMBER` vs `DENSE_RANK` for nth-highest with ties; NVL's garbled definition;
MySQL VARCHAR limits and "CHAR is 50% faster"; 32-bit Unix timestamps; ROUND listed as an
aggregate; TRUNCATE's rollback behaviour stated as universal when it is per-engine; "DDL can never
be rolled back" (false for PostgreSQL and SQL Server).

**Cloud and warehouses** — Redshift said to lack materialised views, UDFs and cross-database
queries, to have immutable sort/dist keys (`ALTER SORTKEY`/`DISTKEY` since 2019) and snapshots
that cannot cross regions; two invented commands (`REINDEX`, `ANALYZE DELETE`); BigQuery said not
to support UPDATE/DELETE and to be eventually consistent; BigQuery flat-rate pricing (retired 2023,
now Editions); S3 Reduced Redundancy; `obenner/azure.md` being almost entirely the retired 2010
Cloud Services platform.

**NoSQL** — Bigtable described as eventually consistent (strong within a single cluster), as
lacking CDC (change streams GA 2023) and data expiry (GC policies exist); Cassandra said to have
no ACID whatsoever (per-partition atomicity plus SERIAL lightweight transactions); HBase's HMaster
as a hard SPOF (ZooKeeper elects standbys).

**Modelling** — OLTP equated with star schema and OLAP with snowflake (backwards: OLTP is
normalised ER, both star and snowflake are OLAP); many-to-many "implemented with a snowflake
schema" (it needs a bridge table); "fact tables have many-to-many relationships with dimensions"
(fact-to-dimension is many-to-one); bitmap indexes described as Oracle-only.

**BI** — Superset cross-database joins in a single query (not supported); `pip install superset`
(now `apache-superset`); Looker on-premises as a normal deployment; Looker called "batch-only".

## Where to pick up

Read `CLAUDE.md` first — it carries the invariants and the validation commands. `README.md` has
the study plan. The likely next task is an Anki deck from the 606 ★ questions.

