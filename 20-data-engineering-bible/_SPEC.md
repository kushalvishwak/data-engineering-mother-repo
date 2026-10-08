# BUILD SPEC — read this fully before writing anything

You are building one part of a linked knowledgebase for data-engineering interview prep.
Target reader: someone interviewing for **data engineering / analyst roles at banks and large
enterprises**, where the rounds lean on SQL basics, scenario design, cloud elasticity,
star vs snowflake and SCD. Assume they can write queries and struggle to *recite definitions*
cold — that asymmetry is the whole reason this vault exists.

## Sources (already downloaded — do NOT fetch the network)

- `_sources/obenner/*.md` — 38 files, each `## heading` is one interview question. Large files:
  `sql.md` 466 Q, `dwha.md` 283 Q, `spark.md` 243 Q, `data-structure.md` 222 Q, `hadoop.md` 207 Q.
- `_sources/devinterview.md` — "Top 100 Data Engineer Interview Questions", `## N. Question` with
  full answers.
- `_sources/cookbook_interview.md` — andkret Cookbook, questions grouped under `### Topic`.

**Never read a whole large file into context.** Use `grep -n '^## ' file` to get the question
index, then `sed -n 'A,Bp'` on the ranges you actually need. Budget: skim, do not study.

## Your output

One markdown file per node you own, at `nodes/<node-id>.md`, using the template below verbatim.
Nothing else. Do not create index files, do not edit other agents' nodes, do not touch
`_sources/`.

## Template

```markdown
---
id: <node-id>
title: <Human Title>
tier: <0|1|2|3|4>
priority: <must-know | should-know | nice-to-have>
sources: [obenner/<files used>, devinterview, cookbook]
---

# <Human Title>

## Say it in one line
<The single sentence that answers "what is this" in an interview. No hedging.>

## Must be able to recite
- **<term>** — <one-sentence answer, contrast + one consequence>
- ... (8–15 items, the highest-frequency facts for this node)

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ <question text> — <answer in 1–2 sentences>
- <question text> — <answer in 1–2 sentences>
... (15–40 items depending on how much the sources carry; merge duplicates across sources,
    rewrite garbled or broken-English question text into clean phrasing, keep the meaning)

## Traps
- <the specific way candidates get this wrong, and the correct move>
(3–6 items)

## Graph
- **Needs first:** [[node-id]], [[node-id]]
- **Leads to:** [[node-id]]
- **Asked together with:** [[node-id]]
(Copy these from the EDGES section of this spec. Use the exact ids — wikilinks must resolve.)
```

## Rules

1. **Answers must be correct.** If a source's answer is wrong or dated, fix it and say so
   inline: `(the source says X; that is outdated — Y is current)`.
2. One sentence per bullet. Two clauses maximum. This is a recall drill, not an essay.
3. Merge across sources: if all three ask "explain star vs snowflake", that is **one** ★ entry.
4. Keep vendor-specific trivia out of Tier-0/1 nodes; it belongs in the cloud nodes.
5. Indian-market context is welcome where it matters (e.g. which tools actually get asked).
6. No fabricated questions. Everything traces to one of the three sources — but you may add a
   maximum of 3 obvious gaps per node, marked `(not in sources, but standard)`.
7. British or American spelling, consistent within your files. Plain prose, no marketing words.

## NODES (canonical ids — never invent one)

Tier 0 — foundations: `sql-semantics` `sql-joins-sets` `sql-aggregation` `sql-window-functions`
`sql-ctes-subqueries` `sql-ddl-dml-transactions` `sql-performance-indexing` `sql-query-patterns`
`relational-modeling` `dimensional-modeling` `scd-history` `warehouse-architecture` `oltp-vs-olap`

Tier 1 — pipelines: `etl-vs-elt` `pipeline-design` `orchestration-airflow` `dbt-transformations`
`cdc-ingestion` `batch-vs-streaming` `kafka-messaging` `lambda-kappa`

Tier 1 — processing: `spark-core` `spark-tuning` `hadoop-hdfs` `mapreduce` `hive-impala`

Tier 1 — storage: `file-formats` `table-formats-lakehouse` `partitioning-layout`
`distributed-systems` `nosql-stores`

Tier 2 — cloud: `cloud-fundamentals` `aws-data-stack` `gcp-bigquery` `azure-data-stack`
`warehouse-engines` `containers-kubernetes` `cost-optimization`

Tier 3 — ops: `data-quality` `data-governance` `observability` `system-design-scenarios`
`behavioral-project-story`

Tier 4 — adjacent: `python-for-data` `dsa-coding` `bi-visualization` `linux-shell` `apis-rest`

## EDGES (copy the lines for your nodes into their Graph section)

| node | needs first | leads to | asked together with |
|---|---|---|---|
| sql-semantics | — | sql-joins-sets, sql-aggregation | sql-ddl-dml-transactions |
| sql-joins-sets | sql-semantics | sql-aggregation, sql-query-patterns | relational-modeling |
| sql-aggregation | sql-semantics | sql-window-functions | dimensional-modeling |
| sql-window-functions | sql-aggregation | sql-query-patterns | sql-performance-indexing |
| sql-ctes-subqueries | sql-semantics | sql-query-patterns | sql-window-functions |
| sql-ddl-dml-transactions | sql-semantics | sql-performance-indexing | relational-modeling, cdc-ingestion |
| sql-performance-indexing | sql-joins-sets, sql-ddl-dml-transactions | partitioning-layout | warehouse-engines |
| sql-query-patterns | sql-window-functions, sql-ctes-subqueries | system-design-scenarios | dsa-coding |
| relational-modeling | sql-ddl-dml-transactions | dimensional-modeling | oltp-vs-olap |
| dimensional-modeling | relational-modeling | scd-history, warehouse-architecture | sql-aggregation, bi-visualization |
| scd-history | dimensional-modeling | cdc-ingestion | dbt-transformations |
| warehouse-architecture | dimensional-modeling | etl-vs-elt, warehouse-engines | table-formats-lakehouse |
| oltp-vs-olap | relational-modeling | warehouse-architecture | nosql-stores, file-formats |
| etl-vs-elt | warehouse-architecture | pipeline-design, dbt-transformations | cloud-fundamentals |
| pipeline-design | etl-vs-elt | orchestration-airflow, data-quality | system-design-scenarios |
| orchestration-airflow | pipeline-design | observability | containers-kubernetes |
| dbt-transformations | etl-vs-elt, dimensional-modeling | data-quality | warehouse-engines |
| cdc-ingestion | sql-ddl-dml-transactions, scd-history | batch-vs-streaming | kafka-messaging |
| batch-vs-streaming | pipeline-design | kafka-messaging, lambda-kappa | spark-core |
| kafka-messaging | batch-vs-streaming | lambda-kappa | distributed-systems |
| lambda-kappa | batch-vs-streaming, kafka-messaging | system-design-scenarios | warehouse-architecture |
| spark-core | distributed-systems | spark-tuning | mapreduce, batch-vs-streaming |
| spark-tuning | spark-core | cost-optimization | partitioning-layout |
| hadoop-hdfs | distributed-systems | mapreduce, hive-impala | file-formats |
| mapreduce | hadoop-hdfs | spark-core | distributed-systems |
| hive-impala | hadoop-hdfs, sql-semantics | warehouse-engines | file-formats, partitioning-layout |
| file-formats | — | partitioning-layout, table-formats-lakehouse | spark-tuning |
| table-formats-lakehouse | file-formats, warehouse-architecture | warehouse-engines | cdc-ingestion |
| partitioning-layout | file-formats | spark-tuning, cost-optimization | sql-performance-indexing |
| distributed-systems | — | spark-core, nosql-stores | kafka-messaging |
| nosql-stores | distributed-systems, oltp-vs-olap | warehouse-engines | system-design-scenarios |
| cloud-fundamentals | — | aws-data-stack, gcp-bigquery, azure-data-stack | cost-optimization, containers-kubernetes |
| aws-data-stack | cloud-fundamentals | warehouse-engines | pipeline-design |
| gcp-bigquery | cloud-fundamentals | warehouse-engines | partitioning-layout |
| azure-data-stack | cloud-fundamentals | warehouse-engines | pipeline-design |
| warehouse-engines | warehouse-architecture, cloud-fundamentals | cost-optimization | sql-performance-indexing |
| containers-kubernetes | cloud-fundamentals, linux-shell | orchestration-airflow | observability |
| cost-optimization | cloud-fundamentals, warehouse-engines | — | partitioning-layout, spark-tuning |
| data-quality | pipeline-design | data-governance, observability | dbt-transformations |
| data-governance | data-quality | — | warehouse-architecture |
| observability | pipeline-design | — | data-quality, orchestration-airflow |
| system-design-scenarios | warehouse-architecture, pipeline-design, batch-vs-streaming | behavioral-project-story | nosql-stores, lambda-kappa |
| behavioral-project-story | system-design-scenarios | — | — |
| python-for-data | — | pipeline-design, dsa-coding | apis-rest, linux-shell |
| dsa-coding | python-for-data | sql-query-patterns | — |
| bi-visualization | dimensional-modeling | — | warehouse-engines |
| linux-shell | — | containers-kubernetes | python-for-data |
| apis-rest | — | pipeline-design | python-for-data |
