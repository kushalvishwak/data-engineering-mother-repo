---
id: sql-performance-indexing
title: Indexing and Query Performance
tier: 0
priority: must-know
sources: [obenner/sql.md, obenner/dwha.md, cookbook]
---

# Indexing and Query Performance

## Say it in one line
An index is a separate sorted structure — almost always a B-tree — that lets the engine jump straight to the rows a predicate needs instead of scanning the table, paid for with slower writes, extra storage and a plan the optimiser may still decide to ignore.

## Must be able to recite
- **B-tree index** — a sorted tree reached root-to-leaf in a handful of page reads, serving equality, range, prefix `LIKE` and `ORDER BY` on the indexed columns.
- **Clustered index** — the table itself held in key order, so the leaf level *is* the data; one per table, and it decides the physical row order.
- **Non-clustered index** — a separate structure whose leaf holds the key plus a row locator (a RID for a heap, the clustered key otherwise); many per table, and each extra hop to the table is a lookup.
- **Which engines actually cluster** — SQL Server's clustered index and InnoDB's primary key do; Oracle heap tables and PostgreSQL have no maintained clustered index (Oracle's index-organised table and Postgres's one-off `CLUSTER` are the nearest things).
- **Covering index** — one that already contains every column the query needs, so the engine never touches the table; built with extra key columns or `INCLUDE` columns.
- **Composite index column order** — leftmost-prefix rule: put equality columns first and the range or sort column last, because a predicate on `b` alone cannot use an index on `(a, b)`.
- **Selectivity** — an index only pays off when the predicate returns a small share of the table; past the tipping point the optimiser correctly prefers a full scan.
- **Sargability** — a predicate is sargable when the indexed column appears bare, so `UPPER(name) = 'RICH'`, `col + 0 = 5`, `LIKE '%rich%'` and implicit type casts all force a scan.
- **Statistics** — the row counts and histograms the cost-based optimiser uses to estimate cardinality; stale statistics after a bulk load or a truncate-and-reload are a leading cause of bad plans.
- **What indexes cost** — every INSERT, UPDATE and DELETE maintains every affected index, so delete and load time rise roughly in proportion to the index count, plus storage and buffer-cache pressure.
- **When not to index** — tiny tables, low-selectivity columns, write-heavy staging tables, and any index the optimiser never chooses, which you still pay for on every write.
- **EXPLAIN** — shows the plan the optimiser picked; compare estimated with actual rows to catch stale statistics, and look for scans of big tables, row lookups and sorts spilling to disk.
- **Unique index** — enforces uniqueness and hands the optimiser a one-row guarantee; primary key and unique constraints are implemented as indexes underneath.
- **Bitmap index** — one bitmap per distinct value, cheap to AND and OR together, excellent on low-cardinality warehouse fact columns and unusable under concurrent OLTP writes.
- **Index the foreign key column on the child side** — otherwise every parent delete or key update scans the child table, and in Oracle takes a share lock on it.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ **Clustered versus non-clustered index, with an example?** — A clustered index stores the rows themselves in key order so there is one per table (think a phone book ordered by surname); a non-clustered index is a separate structure holding the key plus a pointer to the row, so you can have many (think the index at the back of a book).
- ★ **What are the steps to fix a poorly performing query?** — Read the execution plan first, check the cardinality estimates against actuals, make the predicates sargable, add or reorder a covering index, cut the data scanned (fewer columns, partition pruning, filter earlier), and only then consider rewriting the join or shape. *(the sources answer "maximise use of stored procedures and computed columns and avoid cursors" — dated advice that skips the actual diagnosis)*
- ★ **How do you check whether a query is using the index you expect?** — Read the execution plan (`EXPLAIN`, `EXPLAIN ANALYZE`, `EXPLAIN PLAN` plus `DBMS_XPLAN`, or the graphical plan) and look for a seek or index scan on that index rather than a full table scan.
- **What makes a predicate sargable, and how do you rewrite one that is not?** — The indexed column must appear alone on one side, so replace `WHERE YEAR(order_date) = 2024` with `WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01'`, and replace `UPPER(name) = 'RICH'` with a case-insensitive collation or an expression index. *(not in sources, but standard)*
- **What is a covering index, and how do you order the columns of a composite index?** — A covering index contains every column the query references, so the answer comes from the index alone; order the keys equality-first then range/sort, and match the leftmost prefix your queries actually filter on. *(not in sources, but standard)*
- ★ **Do indexes ever hurt, and what is the downside of indexing every column?** — Every index has to be maintained on each write and consumes disk and cache, so an index-per-column table loads and deletes far more slowly while the optimiser gains options it will never use.
- ★ **What are statistics, when do they go stale, and how do you refresh them?** — They describe index selectivity and value distribution for the optimiser; they go stale after a large insert, update or delete, after a truncate-and-repopulate, and after a version upgrade, and you refresh them with `UPDATE STATISTICS`, `ANALYZE` or `DBMS_STATS`.
- ★ **What is an index?** — An optional structure over one or more columns that gives direct access to rows so the engine can retrieve them without scanning the whole table.
- ★ **How many clustered indexes can a table have?** — Exactly one, because a table can only be physically ordered one way; you can have many non-clustered indexes alongside it.
- **What index does `CREATE INDEX myIndex ON myTable(myColumn)` create?** — A non-clustered, non-unique index; the primary key already took the clustered index by default in SQL Server unless you said otherwise.
- **How do you find indexes that are unused or duplicated?** — Read the usage counters (`sys.dm_db_index_usage_stats`, `pg_stat_user_indexes`, `performance_schema` in MySQL), and treat an index whose leading columns are a prefix of another index's as redundant. *(not in sources, but standard)*
- ★ **What indexing would you use on a warehouse fact table?** — Historically bitmap indexes on the low-cardinality dimension keys of the fact table and B-tree or bitmap on the dimensions. *(the source says only Oracle has bitmap indexes — still true; SQL Server's equivalent for fact tables is a clustered columnstore index, and cloud warehouses replace indexes altogether with sort keys, clustering keys and micro-partition pruning)*
- **What kinds of index exist?** — B-tree (the default), unique, composite, covering, filtered/partial, expression or function-based, hash, bitmap, columnstore, full-text, spatial, XML/JSON, and PostgreSQL's GIN, GiST and BRIN. *(the source's list of "binary search, B-tree, inverted list, memory resident table" is textbook-era phrasing for the same idea)*
- **How do you create, list and drop an index?** — `CREATE INDEX ix ON t(col)`, `SHOW INDEX FROM t` (or the catalogue views / `pg_indexes`), and `DROP INDEX ix ON t`.
- **How many columns can go in a composite index?** — MySQL allows up to 16, and every engine has a key-length limit, but useful composite indexes are two to four columns — beyond that the tail columns rarely earn their keep.
- **Are indexes maintained automatically?** — Yes, every relevant DML change is applied to every relevant index in the same transaction, which is precisely why writes get slower as you add indexes.
- **Why do DELETEs get slower as the table gains indexes?** — Each deleted row must be removed from every index, so delete time rises roughly in proportion to the number of indexes, and deleting all rows should be a TRUNCATE instead.
- ★ **What is query optimisation, and what approaches does the optimiser take?** — It is the phase that picks the cheapest execution plan; historically rule-based (fixed precedence of access paths) versus cost-based (estimates from statistics), and every current engine is cost-based.
- **What does ANALYZE do?** — Gathers statistics about a table, index or cluster into the data dictionary for the optimiser, and can also validate structure and find chained or migrated rows.
- **Why is filtering in the WHERE clause faster than filtering in the report or a format trigger?** — The database can use an index and returns fewer rows, whereas a downstream filter makes the engine read and ship everything before discarding it — push predicates as close to the storage as you can.
- **How does the engine optimise `DISTINCT`?** — It is rewritten as a GROUP BY on all selected columns, usually needs a sort or hash (and a temporary table when combined with `ORDER BY`), and with `LIMIT` it can stop as soon as it has enough unique rows.
- **How does the engine optimise `LIMIT`?** — It stops as soon as enough rows are produced, will pick an index over a scan to avoid sorting, and ends a sort early once the first *n* rows are ordered — but a deep `OFFSET` still walks and throws away everything it skips.
- **What is an index segment, and how is an index stored?** — Its own storage structure separate from the table data (an index segment made of extents in Oracle terms), which is why indexes consume disk in their own right.
- **What is a cluster and a cluster key?** — Tables physically stored together because they share columns that are always queried together, keyed by the shared columns, with the key value stored once for all the tables in the cluster; an index cluster is one with an index on that key.
- **What is collation, and how can it stop an index being used?** — Collation is the rule set for comparing and sorting character data, including case and accent sensitivity; comparing two columns with different collations forces a conversion that makes the predicate non-sargable.
- **What is denormalisation, and when do you accept it?** — Controlled redundancy — pre-joined or pre-aggregated columns — to cut the number of joins a read has to do, accepted when read performance matters more than the duplicate-update risk, which is the normal trade in reporting layers.
- **What is a filtered or partial index?** — An index with a WHERE clause, so it only covers the rows you actually query (for example active orders); it is smaller, cheaper to maintain and often the fix for a lopsided predicate.
- **What is sharding?** — Splitting rows of one logical table across several databases or servers by a shard key, so each holds a slice; it buys horizontal scale at the cost of cross-shard joins and rebalancing.
- **How do you speed up a bulk load?** — Drop or disable the non-essential indexes and constraints, load, then rebuild and update statistics, because maintaining every index row by row during the load is what makes it slow.

## Traps
- Reciting "a clustered index physically sorts the table" for PostgreSQL or Oracle, where no such maintained index exists — the concept is SQL Server and InnoDB.
- Adding one index per column instead of one composite index in the order the queries filter — three single-column indexes rarely replace `(a, b, c)`.
- Wrapping the indexed column in a function or a cast and still expecting a seek.
- Assuming an index always helps: on a low-selectivity predicate the row lookups cost more than a scan, and the optimiser will and should ignore your index.
- Forgetting that InnoDB secondary indexes store the primary key as the row pointer, so a wide or random primary key bloats and fragments every other index.
- Mixing up the two meanings of heap: in MySQL a HEAP table is the in-memory engine, in SQL Server a heap is simply a table with no clustered index.

## Graph
- **Needs first:** [[sql-joins-sets]], [[sql-ddl-dml-transactions]]
- **Leads to:** [[partitioning-layout]]
- **Asked together with:** [[warehouse-engines]]
