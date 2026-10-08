---
id: sql-ctes-subqueries
title: CTEs, Subqueries, Views and Temp Tables
tier: 0
priority: must-know
sources: [obenner/sql.md, obenner/dwha.md, cookbook]
---

# CTEs, Subqueries, Views and Temp Tables

## Say it in one line
A subquery is a query nested inside another statement, a CTE is that same subquery given a name up front with `WITH` so it can be read top-down and reused, and neither stores anything — unlike a temp table or a materialised view, which do.

## Must be able to recite
- **Subquery** — a SELECT nested inside another statement whose result feeds the outer query's filter, column list or FROM clause, and which lives only for that statement.
- **Three shapes of subquery** — scalar (one row, one column, usable anywhere a value is), multi-row (feeds `IN`/`ANY`/`ALL`), and derived table (sits in FROM and must be aliased).
- **Correlated subquery** — references a column of the outer query, so it is logically evaluated once per outer row; you spot it by the outer alias appearing inside its WHERE.
- **CTE** — a named subquery declared in a `WITH` clause before the main statement, scoped to that statement only, used to make multi-step logic readable and to reference one result twice.
- **Recursive CTE** — `WITH RECURSIVE t AS (anchor query UNION ALL member query referencing t)`, used for hierarchies, date spines and graph walks, and it needs a termination condition.
- **CTE is not a temp table** — it is not stored, not indexed and has no statistics, so a huge intermediate result reused many times belongs in a temp table instead.
- **Optimisation fence** — Postgres materialised every CTE before v12 and inlines them now unless you write `AS MATERIALIZED`, so never promise an interviewer that a CTE is evaluated exactly once.
- **Temp table** — a real table scoped to the session (`#t` in SQL Server, `CREATE TEMPORARY TABLE` elsewhere) that can be indexed and analysed, and disappears on disconnect.
- **Heap table (MySQL MEMORY engine)** — an in-memory table that is shared between clients and survives disconnect but not a restart, whereas a temp table is private to one session.
- **View** — a stored named SELECT that holds no data and re-executes on every reference, so it costs exactly what pasting the query would cost.
- **Materialised view** — stores the query result physically, so reads are fast but the data is as stale as the last refresh, and it consumes space.
- **Refresh modes** — complete (re-run the whole query) or fast/incremental (apply only logged changes); Oracle's snapshot log, and modern engines' change logs, are what make fast refresh possible.
- **EXISTS** — a semi-join that stops at the first matching row and returns true or false, which is the right operator for "does a related row exist".
- **NOT IN with NULLs** — one NULL in the subquery makes `NOT IN` return no rows at all, while `NOT EXISTS` and `LEFT JOIN ... IS NULL` stay NULL-safe.
- **Anti-join shapes** — `NOT EXISTS`, `LEFT JOIN ... WHERE b.key IS NULL`, and `EXCEPT`/`MINUS` all answer "in A but not in B"; `EXCEPT` additionally compares whole rows and removes duplicates.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ **View vs materialised view?** — A view stores only the SQL and re-runs it on every access; a materialised view stores the result set physically, so it answers instantly but is stale until refreshed and occupies space.
- **What is a CTE and when would you use one instead of a subquery?** — Same result, better shape: `WITH` names each step, lets you reference a step twice, and reads top-down, so use it for multi-step logic and use a plain subquery for a one-off filter. *(not in sources, but standard)*
- **Write a recursive CTE to walk an employee-manager hierarchy.** — Anchor on the root (`WHERE manager_id IS NULL`), `UNION ALL` a member that joins employees to the previous level, and carry a `level + 1` counter as both output and stop guard. *(not in sources, but standard)*
- **EXISTS vs IN vs JOIN — which do you use?** — `EXISTS` for a pure existence test, `IN` for a small literal or NULL-free list, and a JOIN when you actually need columns from the second table; a JOIN can also multiply rows if the key is not unique. *(not in sources, but standard)*
- ★ **What is a correlated subquery, and how do you identify one?** — It references the outer query's columns, so it is conceptually re-run per outer row; if the same work can be done with a window function or a join, do that instead at scale.
- **Find rows in table A that are not in table B without using NOT IN.** — `SELECT * FROM a EXCEPT SELECT * FROM b` (`MINUS` in Oracle), or the NULL-safe `NOT EXISTS`, or `LEFT JOIN b ... WHERE b.key IS NULL`.
- ★ **What is a subquery?** — A query inside another query whose return value is used by the outer statement, usually to filter it.
- ★ **What is a view?** — A named virtual table backed by a SELECT over one or more real tables, with rows and columns but no storage of its own.
- ★ **Does a view contain data?** — No; only the definition is stored, and the underlying tables are read each time the view is used.
- ★ **What are the advantages of a view?** — It restricts access to chosen rows and columns, hides join and aggregation complexity behind a simple name, and gives every consumer one agreed definition.
- **How do you grant a user access to some columns only?** — Create a view exposing just those columns and `GRANT SELECT` on the view rather than on the base table.
- ★ **Can a view be built on another view?** — Yes, and it is common; the cost compounds, because every layer re-executes, so deep stacks are where "the view is slow" complaints come from.
- **How do you create and drop a view?** — `CREATE [OR REPLACE] VIEW v AS SELECT ...` and `DROP VIEW v`.
- ★ **What is a snapshot, and how is it refreshed?** — A periodically refreshed read-only copy of a remote master table, refreshable `COMPLETE`, `FAST` (via the snapshot log) or `FORCE` (fast if possible, else complete). *(the sources call these snapshots; Oracle renamed them materialised views in 8i — same object)*
- **What is a snapshot log and why does it matter?** — A table beside the master that records which rows changed, which is what allows an incremental (fast) refresh instead of rebuilding the whole result — the same idea as change data capture.
- **Simple vs complex snapshot?** — Simple means no joins, GROUP BY, CONNECT BY or subqueries, and only a simple snapshot can be fast-refreshed; anything more complex needs a full rebuild.
- ★ **Heap table vs temporary table (MySQL)?** — Heap/MEMORY tables live in memory, are visible to all clients and are cleared on restart; temporary tables are private to one session and vanish when it disconnects.
- **What are the limits of a MySQL MEMORY table?** — No TEXT or BLOB columns, no AUTO_INCREMENT, index columns must be NOT NULL, and size is capped by `max_heap_table_size`.
- **How do you create a table with the same structure as an existing one?** — `CREATE TABLE new LIKE old` in MySQL, or `SELECT * INTO new FROM old WHERE 1=0` in SQL Server. *(the source answers `CREATE TABLE std AS SELECT * FROM student`; that copies the data too and carries over no indexes, keys or constraints)*
- ★ **What is a stored procedure and why use one?** — A named, precompiled block of SQL stored in the database that takes parameters and returns values or result sets; it centralises logic, cuts round trips and can be granted independently of the tables.
- **Get the nth highest salary using a subquery.** — `SELECT * FROM emp e1 WHERE (n-1) = (SELECT COUNT(DISTINCT e2.salary) FROM emp e2 WHERE e2.salary > e1.salary)` — a correlated subquery counting how many distinct salaries beat each row.
- **Explain the view selection problem.** — Deciding which aggregates are worth materialising: you cannot pre-compute every combination, so you pick the views that serve the most queries for the least storage and refresh cost.
- **What is a CSV table?** — A table whose data is a comma-separated file; it cannot be indexed, which is why it only suits import and export.

## Traps
- Calling a CTE "a temp table" — it stores nothing, has no indexes and no statistics; say "a named subquery" and you will not be caught out.
- Claiming a view makes queries faster — a plain view is pure text substitution; if you need speed you need a materialised view, a temp table or an index.
- Assuming a CTE is computed once — Postgres 12+ inlines it, and it can be re-executed per reference, so measure before relying on it as a cache.
- Answering "in A, not in B" with `NOT IN` and a nullable column — one NULL silently returns zero rows; reach for `NOT EXISTS`.
- Writing a recursive CTE with no stop condition — SQL Server caps it at 100 levels by default, but Postgres and MySQL will happily loop forever on cyclic data.
- Reaching for a correlated subquery in the SELECT list over a large table when a window function does the same work in one pass.

## Graph
- **Needs first:** [[sql-semantics]]
- **Leads to:** [[sql-query-patterns]]
- **Asked together with:** [[sql-window-functions]]
