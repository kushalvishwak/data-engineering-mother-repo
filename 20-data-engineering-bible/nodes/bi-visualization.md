---
id: bi-visualization
title: BI and Visualisation
tier: 4
priority: should-know
sources: [obenner/looker.md, obenner/tableau.md, obenner/superset.md, devinterview, cookbook]
---

# BI and Visualisation

## Say it in one line
A BI tool is a semantic layer plus a chart renderer — it turns a star schema into governed, reusable metrics and pushes every calculation it can down into the warehouse.

## Must be able to recite
- **BI tool** — software that connects to a warehouse, models it into business terms, and lets non-engineers explore and chart it without writing SQL.
- **Semantic layer** — one central definition of dimensions, measures and joins, so "revenue" means the same thing in every dashboard instead of being re-derived per report.
- **Dimension vs measure** — a dimension is a qualitative attribute you slice and group by, a measure is a numeric value that gets aggregated; the same column can be both depending on the role you give it.
- **LookML** — Looker's modelling language, files that declare views (a table plus its dimensions and measures) and explores (a starting table plus its permitted joins), all version-controlled in Git.
- **PDT (persistent derived table)** — a derived table Looker materialises in the warehouse on a schedule or trigger, used to make an expensive calculation cheap to query.
- **Symmetric aggregates** — Looker's trick of hashing primary keys inside the aggregation so a one-to-many join does not double-count the fact measure. *(not in sources, but standard)*
- **Extract vs live (Tableau)** — a live connection queries the source on every interaction, an extract (`.hyper`, previously `.tde`) is a compressed snapshot Tableau queries locally and refreshes on a schedule.
- **Three Tableau calculation types** — basic calculations run row-level or aggregate in the source, LOD expressions (`FIXED`/`INCLUDE`/`EXCLUDE`) compute at a granularity other than the view, and table calculations run on the returned result after the query.
- **Context filter** — a Tableau filter that runs first and produces a temporary subset, so dependent filters and top-N calculations apply to that subset rather than the whole source.
- **Joins vs blending (Tableau)** — a join combines tables inside one data source at row level, blending combines two separate data sources at aggregate level on a linking field.
- **Superset dataset** — a physical table or a saved SQL query ("virtual dataset") that charts point at; charts (historically "slices") are saved visualisations, and a dashboard arranges them with filters.
- **Superset caching** — query results are cached keyed by the query and its parameters, served from cache until the timeout expires or someone force-refreshes.
- **Row-level security** — a per-user or per-role predicate injected into every query, so one dashboard shows each region only its own rows.
- **Chart choice** — bar for comparing categories, line for change over time, scatter for correlation, table for exact lookup, and avoid pie beyond two or three slices.
- **Star schema is why BI is fast** — one central fact table joined directly to conformed dimensions means simple one-hop joins, predictable aggregation, and field names business users recognise.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ What is a BI tool, and what should it not be used for? — It models and visualises data already in the warehouse; it is not an ETL tool, so heavy transformation belongs upstream in SQL, dbt or Spark.
- ★ What is a star schema and why do BI tools prefer it? — A central fact table surrounded by dimension tables, giving simple joins, predictable query patterns and names a business user understands; see [[dimensional-modeling]].
- ★ Dimension versus measure — explain with an example. — Region, product and date are dimensions you group by; sales amount and order count are measures that get summed or averaged per dimension combination.
- ★ My dashboard takes 90 seconds to load — how do you fix it? — Find the generated SQL first, then fix it upstream: pre-aggregate into a mart or PDT, partition and cluster the underlying table, cut the number of separate queries per dashboard, reduce returned rows, and only then rely on caching. *(not in sources, but standard)*
- What is a LookML model? — A collection of files describing views, joins, dimensions and measures, which Looker compiles into SQL at query time; it is the semantic layer as code.
- What is a Looker Explore, and how does it relate to joins? — An Explore is a curated starting point for exploration; the join declarations inside it decide which tables can be brought in and with what relationship.
- ★ What are PDTs and when would you use one? — Persistent derived tables materialised in the warehouse for expensive or repeated logic, rebuilt on a schedule or a trigger; use them when the same derived table is being recomputed for every user.
- ★ How would you optimise Looker performance? — Reduce the number of queries per dashboard, use PDTs and aggregate awareness for expensive logic, lean on caching policies, and fix the warehouse side with partitioning, clustering and statistics.
- How does Looker caching work? — Query results are cached and reused until the cache policy expires or the underlying data is declared changed, with the policy set per model according to how volatile the data is.
- Does Looker store your data? — No, it holds only the model and cached results and issues SQL against the warehouse, so storage, scale and freshness are all properties of the warehouse.
- Can Looker do real-time analysis? — It is only as fresh as the table it queries, so with a streaming-fed table it is near real-time; the source's claim that Looker is a batch-only tool is misleading — it does not store data at all.
- How is LookML change-managed? — LookML lives in Git with branches, diffs and reverts, and developers work in Development Mode so production users are unaffected until changes are deployed.
- What is SQL Runner used for? — Writing ad-hoc SQL directly against the connection to prototype, inspect the SQL Looker generated, or debug a model without going through LookML.
- What is Liquid templating in LookML for? — Injecting conditional logic into generated SQL or field labels, for example switching a table name or a filter based on the user's attributes.
- What are the limitations of Looker? — It needs a performant warehouse underneath, it is not a transformation tool, and modelling is a developer skill; also note that new deployments are Google-hosted (the source's claim that on-premises is a normal option is dated).
- ★ Live connection or extract in Tableau — how do you choose? — Live when the source is fast and freshness matters, extract when the source is slow, remote or being hammered by many users; an extract is a snapshot, so it is stale until the next scheduled refresh.
- What filter types does Tableau have, and in what order do they apply? — Extract, data source, context, dimension, measure and table-calculation filters, applied roughly in that order — which is why a context filter changes what a top-N or table calculation sees.
- ★ What is a calculated field, and what are the three kinds of calculation? — A user-defined field built from other fields; basic calculations at source level, LOD expressions for a different granularity than the view, and table calculations applied to the query result.
- ★ Joins or blending in Tableau — when do you use which? — Joins for tables within the same data source, blending for combining separate sources at aggregate level on a common field, with one primary and one secondary source.
- What does "Assume Referential Integrity" do? — It tells Tableau that every fact row has a matching dimension row, so joined tables can be dropped from the query when no field from them is used, which speeds queries but silently loses rows if the assumption is false.
- Continuous versus discrete fields in Tableau? — Discrete (blue) fields produce headers and can be sorted, continuous (green) fields produce an axis; this is a display role and is independent of whether the field is a dimension or a measure.
- What are sets versus groups? — A set is a conditional or manual subset of a dimension's members that can update dynamically, a group is a static bucketing of members into a coarser category.
- What are the Tableau file types? — `.twb` workbook, `.twbx` packaged workbook with data, `.tds`/`.tdsx` data source, `.hyper` (formerly `.tde`) extract, `.tbm` bookmark.
- What is an extract schedule on Tableau Server? — A server-managed refresh of a published extract, so the snapshot is rebuilt on a cadence rather than by hand.
- Published versus embedded data source? — A published data source lives independently on the server and can be reused and governed centrally; an embedded one is bound to a single workbook and gets duplicated.
- What are dual axes and when do you use them? — Two measures on independent axes in one chart to compare different scales, such as revenue against conversion rate.
- Heat map versus tree map? — A heat map encodes a measure as colour across a dimension grid, a tree map encodes it as nested rectangle area and shows hierarchy.
- Show the top five and bottom five by sales in one view. — Rank the measure with a calculated field or table calculation and filter to ranks in the top and bottom bands, rather than applying two conflicting top-N filters.
- What are the Tableau rank functions? — `RANK` (ties share a rank, then skip), `RANK_DENSE` (ties share, no skip), `RANK_MODIFIED` and `RANK_UNIQUE` (every row a distinct rank) — the same semantics as SQL's ranking window functions.
- What is a parameter in Tableau? — A user-controlled variable (number, string or date) substituted into calculations, filters or reference lines, so a threshold can be changed without editing the workbook.
- How do you load-test a Tableau deployment? — With TabJolt, replaying user-specified loads against the server to size it for concurrency; the source's rule of thumb is a few times a year or after any major content or upgrade change.
- ★ Why would you not choose Tableau? — Licence and maintenance cost, weaker centralised data-level security than a modelled semantic layer, and thin enterprise reporting features; in Indian enterprise and banking interviews the comparison is usually against Power BI and Qlik rather than Cognos.
- What is Apache Superset and how does it differ? — An open-source, Python-based BI tool with SQL Lab, datasets and dashboards; it is free and extensible, but you operate it yourself and its semantic layer is thinner than Looker's.
- What are a Superset dataset, chart and dashboard? — A dataset is a physical or virtual (saved SQL) table, a chart (legacy name "slice") is one saved visualisation of it, and a dashboard arranges charts with shared filters.
- How does Superset handle caching and cache invalidation? — Results are cached per query and parameters and served until the configured timeout expires or the cache is cleared, which is also the honest answer to "how does it handle large datasets" — the database does the work.
- How do you optimise query performance in Superset? — Aggregate in the database, index or partition the underlying tables, keep dataset SQL simple, and set sensible cache timeouts; Superset itself only generates and issues SQL.
- How is Superset secured? — Role-based access control over datasets, charts and dashboards, external auth via LDAP, OAuth or a database backend, and row-level security filters applied per role.
- Can Superset join across two different databases in one query? — No, a query runs against one database connection; the source's "yes" is wrong — cross-source joins have to happen upstream in the warehouse or lake.
- How does Superset schedule reports and integrate with Airflow? — Alerts and report emails run on Celery workers, and Airflow is used to build the tables Superset reads and to refresh caches after a load completes.
- Which chart do you use for which question? — Bar for comparison across categories, line for a trend over time, scatter for relationship between two measures, table for exact values, map for geography; avoid dual axes and pie charts when a bar chart answers it. *(not in sources, but standard)*

## Traps
- Trying to fix a slow dashboard inside the BI tool. Read the generated SQL and fix the model, the grain, the partitions or the aggregate table — the tool is only issuing queries.
- Saying an extract gives real-time data. An extract is a snapshot and is stale between refreshes; a live connection is the real-time option, at the cost of load on the source.
- Ignoring join fan-out. Joining a fact table to another fact or to a one-to-many dimension duplicates rows and inflates every `SUM`; the fixes are the correct grain, symmetric aggregates or pre-aggregation.
- Calling Looker, Tableau or Superset an ETL tool. They transform at query time for presentation; persistent transformation belongs in [[dbt-transformations]] or the pipeline.
- Defining the same metric separately in five dashboards. That is the whole reason the semantic layer exists, and "which number is right" is the question the business will ask.
- Naming raw table and column names in front of business users. Dimensional modelling plus a semantic layer exists so that "Order Date" and "Net Revenue" are what they see.

## Graph
- **Needs first:** [[dimensional-modeling]]
- **Leads to:** —
- **Asked together with:** [[warehouse-engines]]
