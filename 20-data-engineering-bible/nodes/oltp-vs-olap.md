---
id: oltp-vs-olap
title: OLTP vs OLAP
tier: 0
priority: must-know
sources: [obenner/dwha, devinterview, cookbook]
---

# OLTP vs OLAP

## Say it in one line
OLTP systems run huge numbers of small, short, write-heavy transactions against a normalised current-state schema; OLAP systems run a small number of large read-only scans and aggregations across denormalised historical data.

## Must be able to recite
- **OLTP** — online transaction processing: high-concurrency inserts, updates and deletes plus indexed point lookups, answered in milliseconds, ACID per transaction, normalised to 3NF, current state only, so it is the system of record and cannot afford long queries.
- **OLAP** — online analytical processing: ad-hoc aggregations over months or years of history, answered in seconds to minutes, few concurrent users, denormalised dimensional model, append-mostly, so consistency is per load batch rather than per row.
- **The axis list to recite** — purpose, users, query pattern, data volume, data age, schema and normalisation, index strategy, concurrency, consistency model, and the metric each is measured by (transactions per second versus scan throughput).
- **Why you cannot just query the OLTP database** — analytical queries are long and complex, so they hold locks and starve the transactional workload; the OLTP schema is normalised (many joins), is sized for current data, and keeps no history to trend against.
- **Row store** — all columns of a row are stored contiguously, so writing or fetching a whole row is one I/O; ideal for OLTP point reads and writes, and terrible at scanning three columns out of two hundred because it reads every byte of every row.
- **Column store** — each column is stored contiguously, so a query reads only the columns it names and compresses far better because the values in one column are homogeneous (run-length, dictionary and delta encoding); low-cardinality columns compress to almost nothing, which is why analytical scans are cheap.
- **Consequences of columnar** — `SELECT *` throws away the whole advantage, and a single-row update means rewriting a compressed block, which is exactly why lakehouse table formats need copy-on-write or merge-on-read machinery for upserts.
- **HTAP** — hybrid transactional/analytical processing: one system serving both, normally by keeping a row store for writes plus a synchronously maintained column-store replica for reads, so you avoid a separate ETL hop at the cost of a much more expensive engine.
- **Cube** — a multidimensional structure whose edges are dimension members and whose cells hold measures; the base cuboid is the finest grain and the surrounding cuboids are pre-aggregations along subsets of the dimensions.
- **MOLAP** — measures pre-aggregated into a proprietary multidimensional store with the joins already resolved; fastest queries and the classic form of OLAP, but it needs a build/refresh step and hits a size ceiling.
- **ROLAP** — the cube stays as a star schema in a relational database and every aggregation is computed at query time in SQL; it scales to any volume and needs no build step, but each query costs more and it depends entirely on good schema design and aggregate tables.
- **HOLAP and DOLAP** — HOLAP keeps detail rows relational and pre-computes only the aggregates multidimensionally; DOLAP extracts a small cube to a single analyst's desktop, which today means a Power BI or Tableau local extract rather than a separate product category.
- **Cube operations** — slice (fix one dimension), dice (filter several), drill-down and roll-up (move along a hierarchy), pivot (rotate the axes), and drill-across (combine two fact tables through their conformed dimensions).
- **Pre-aggregation and the view selection problem** — sub-second OLAP comes from materialised aggregates at chosen combinations of dimension granularities; you cannot materialise every cuboid, so view selection is the exercise of choosing which ones pay for themselves.
- **Indexing an analytical store** — the classic answer was bitmap indexes on low-cardinality fact foreign keys plus a star transformation (one bitmap per distinct value, ANDed together, with binning or alternative encodings to save space); modern cloud columnar engines expose no indexes at all and rely on column pruning, compression, partitioning, clustering and min-max/zone-map statistics instead.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ What is the difference between OLTP and OLAP? — OLTP: day-to-day transactions, real-time writes, simple standardised queries, normalised schema, ACID, current data, thousands of concurrent users. OLAP: reporting and analysis, periodic loads, complex ad-hoc aggregations, denormalised dimensional schema, historical data, few users running heavy scans. Both are usually relational; the difference is the workload, not the technology. (One source says OLTP means a star schema and OLAP means a snowflake schema — that is simply wrong. OLTP is normalised ER; star *and* snowflake are both OLAP designs.)
- ★ Is an OLTP database design optimal for a data warehouse? — No. Its tables are normalised so every analytical query pays for extra joins, it is sized for current data and holds no multi-year history, and a heavy analytical query on it degrades the transactional workload the business depends on.
- ★ What is a row store, what is a column store, and what is the difference? — A row (or key-value) store keeps all of a row's columns together, so whole-row reads and writes are one operation, which suits point lookups and OLTP. A column store keeps each column together, so a query reads only the columns it references and compresses much better, which suits scans and aggregation. Row stores lose on wide-table scans, column stores lose on single-row updates.
- ★ Explain OLAP, MOLAP, ROLAP, DOLAP and HOLAP. — OLAP is the category: multidimensional collection, storage and analysis of data. MOLAP stores the cube in a proprietary multidimensional structure with joins pre-resolved, so it is fastest but must be built. ROLAP leaves the data in relational star schemas and computes aggregations in SQL at query time, so it scales further but each query costs more. HOLAP splits the two: relational detail, multidimensional aggregates. DOLAP is a desktop-sized cube extract for one user.
- ★ What is a cube, and where is cube technology used? — A logical multidimensional structure whose edges hold dimension members and whose body holds measures; it is used for interactive multi-dimensional decision-support querying, and it consists of a base cuboid at the finest grain surrounded by cuboids aggregated along one or more dimensions.
- Explain the functionality of OLAP. — A hypercube of measures arranged by dimensions sits at the core; its metadata is derived from a star or snowflake schema, with dimensions read from the dimension tables and measures from the fact table.
- What is OLAP in business intelligence? — The server layer between the BI client and the database that understands how the data is organised, generates the aggregation SQL, and provides analytical functions such as time series, period-over-period and trend views.
- Explain aggregations in OLAP and why they are needed. — Sub-second responses on large data come from pre-aggregating measures along the dimensions; the set of candidate aggregations is the combination of dimension granularities, which is why the count of possible aggregates explodes.
- What is the view selection problem? — Computing and storing every possible aggregate is impossible, so you choose which aggregate views to materialise based on query patterns and cost; that choice is the view selection problem.
- What role do bitmap indexes play in solving aggregation problems? — In a star schema they let the engine intersect low-cardinality dimension filters as bit arrays before touching the fact rows, which is far cheaper than joining large to small repeatedly; they are strongest on columns like gender or status flags.
- What encoding technique is used in bitmap indexes? — By default one bitmap per distinct value; alternative encodings reduce the number of bitmaps and so the space, at the cost of having to read several bitmaps per query.
- What is binning? — Grouping multiple values into one bin so a single bitmap or bucket covers a range; it saves space but query time becomes variable, since a query answered inside a bin may still need to re-check the rows.
- What indexing mechanism do you need for a typical data warehouse? — Classically bitmap indexes on the fact table's foreign keys, plus B-tree or bitmap indexes on dimensions. (The source's claim that only Oracle supports bitmaps is outdated, and more importantly the modern cloud engines — BigQuery, Snowflake, Redshift — expose no indexes at all: you tune with partitioning, clustering/sort keys, column pruning and zone-map statistics.)
- Which technology should be used for interactive querying across multiple dimensions for decision making? — The source answers MOLAP, which was right for its era. Cubes still exist (SSAS, Essbase), but the current default is a columnar MPP warehouse over a star schema with a semantic layer on top; say both and explain why the trade-off moved.
- What is a linked cube? — A cube in which a subset of another cube's data can be analysed in detail, with the link keeping the two consistent so drill-through does not contradict the summary.
- What are the multidimensional features of OLAP? — Support for multiple hierarchies over the same data so the same measure can be analysed by several independent paths (product category and product supplier, calendar and fiscal time) without restructuring the model.
- What is the difference between an ETL tool and an OLAP tool? — An ETL tool moves and transforms data into the warehouse; an OLAP tool sits on top of the loaded warehouse and serves aggregated multi-dimensional queries and reports. The output of the ETL tool is the input of the OLAP tool.
- What is HTAP? — Hybrid transactional/analytical processing: architectures that serve both workloads from one system, so you get analytics on fresh transactional data without a separate warehouse load, at the cost of engine complexity and price.
- Why does OLTP need ACID while OLAP can tolerate eventual consistency? — Every OLTP transaction represents a real-world commitment (a payment, a booking) and must be atomic and durable; an OLAP report is read as of a load boundary, so a few minutes of lag changes a trend line by nothing.
- What is data mining and how does it differ from OLAP reporting? — OLAP answers questions you already know how to ask by aggregating along dimensions; mining searches for previously unknown patterns and builds predictive models, which is why it estimates future revenue or churn where traditional aggregate reporting only describes the past.
- What do slice, dice, drill-down, roll-up and pivot mean? — Slice fixes one dimension to a single value, dice filters several dimensions to subsets, drill-down moves to a finer level of a hierarchy, roll-up moves to a coarser one, and pivot rotates which dimensions form the axes. (Drill-down and drill-across are in the sources; the full slice/dice/pivot vocabulary is not, but it is standard.)

## Traps
- Saying "OLTP uses a star schema" — some interview material prints exactly this and it is wrong; OLTP is normalised ER, and star and snowflake are both OLAP schemas.
- Reducing OLAP to "reporting" — the distinguishing properties are workload shape (few very large scans), history depth and denormalisation, not the presence of a dashboard.
- Claiming columnar storage is faster for everything — it loses badly on single-row lookups and row-level updates, and that limitation is why Iceberg, Delta and Hudi need copy-on-write and merge-on-read strategies.
- Reciting MOLAP/ROLAP/HOLAP without saying where the bytes physically live — MOLAP is a proprietary multidimensional store, ROLAP is a relational star, HOLAP splits detail from aggregates. That location *is* the answer.
- Answering "MOLAP" to a modern interactive-analytics design question — name the cube option, then say what you would actually build today (columnar MPP warehouse plus semantic layer) and why.
- Ignoring concurrency — OLTP means thousands of users doing tiny units of work, OLAP means a handful doing enormous ones; that contrast is the reason the two workloads have to be physically separated, and it is often the point of the question.

## Graph
- **Needs first:** [[relational-modeling]]
- **Leads to:** [[warehouse-architecture]]
- **Asked together with:** [[nosql-stores]], [[file-formats]]
