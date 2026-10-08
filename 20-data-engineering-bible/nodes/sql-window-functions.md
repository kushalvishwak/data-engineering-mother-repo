---
id: sql-window-functions
title: Window Functions
tier: 0
priority: must-know
sources: [obenner/sql.md, obenner/redshift.md, obenner/greenplum.md, obenner/bigquery.md, cookbook]
---

# Window Functions

## Say it in one line
A window function computes an aggregate or a ranking over a set of rows related to the current row and returns one value for every input row, so unlike GROUP BY it summarizes without throwing the detail away.

## Must be able to recite
- **Window function** — an aggregate or ranking evaluated over a frame of rows around the current row, producing a value per row instead of per group.
- **OVER clause** — three optional parts: PARTITION BY to restart the calculation, ORDER BY to sequence rows inside the partition, and the frame to say which rows count.
- **PARTITION BY vs GROUP BY** — PARTITION BY splits rows for the calculation but keeps all of them in the output, GROUP BY collapses them.
- **Default frame** — with ORDER BY it is `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`, which is why `SUM(x) OVER (ORDER BY d)` is a running total; with no ORDER BY the frame is the whole partition.
- **ROWS vs RANGE** — ROWS counts physical rows, RANGE includes every peer row sharing the current ORDER BY value, so with duplicate dates RANGE jumps the running total to the end of the tie.
- **ROW_NUMBER()** — a unique sequence per partition with an arbitrary tie-break, the workhorse for de-duplication and pagination.
- **RANK() vs DENSE_RANK()** — both give ties the same number, RANK then skips (1, 2, 2, 4) while DENSE_RANK does not (1, 2, 2, 3), so "nth highest distinct value" is `DENSE_RANK() = n`.
- **NTILE(n)** — splits the partition into n buckets as evenly as possible, with the earlier buckets taking the extra rows.
- **LAG / LEAD(col, offset, default)** — the value from an earlier or later row in the partition, which gives period-over-period deltas and gap detection without a self-join.
- **FIRST_VALUE / LAST_VALUE / NTH_VALUE** — a value at a position in the frame, and LAST_VALUE with the default frame returns the current row, so it needs `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`.
- **Moving average** — `AVG(x) OVER (PARTITION BY k ORDER BY d ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)` for a trailing seven-period mean.
- **ROW_NUMBER patterns** — `= 1` with `PARTITION BY group ORDER BY metric DESC` gives top-N per group, and the same shape with `ORDER BY updated_at DESC` keeps the latest row per key.
- **Evaluation timing** — windows run after WHERE, GROUP BY and HAVING and before ORDER BY, so they can consume aggregates but cannot be referenced in WHERE or HAVING.
- **Filtering a window result** — wrap the query in a CTE or subquery and filter outside; Snowflake, BigQuery, Teradata and DuckDB offer QUALIFY as the shortcut.
- **Cost** — a window needs its input sorted by PARTITION BY plus ORDER BY, so reusing one OVER specification (or a named WINDOW clause) across several columns avoids repeated sorts.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ What are windowing (analytic) functions, and how do they differ from GROUP BY? — they compute over a set of rows related to the current row and return one value per row, so the detail survives; note that one source calls DISTINCT and GROUP BY "window functions", which is wrong — those collapse rows and take no OVER clause.
- ★ Write a query to get the nth (say, second) highest salary. — `DENSE_RANK() OVER (ORDER BY salary DESC) = n` for the nth distinct salary; the source's `ROW_NUMBER() … = n` returns the nth row instead, which is a different answer as soon as two salaries tie.
- ★ What is the difference between ROW_NUMBER, RANK and DENSE_RANK? — ROW_NUMBER never repeats a number, RANK repeats it and then skips, DENSE_RANK repeats without skipping; choose by whether ties should share a place and whether the next place should jump.
- ★ Get the highest-paid employee in each department, not just the highest salary. — `ROW_NUMBER() OVER (PARTITION BY dept_id ORDER BY salary DESC)` in a subquery, filtered to 1 outside it, because a window function cannot be used in WHERE and `MAX() … GROUP BY` gives you the salary without the rest of the employee's row.
- ★ How do you find duplicates and keep only the latest row per key? — number the rows with `ROW_NUMBER() OVER (PARTITION BY business_key ORDER BY updated_at DESC)` and keep number 1; warehouses such as BigQuery have no built-in de-duplication, so this query *is* the de-duplication step in the pipeline.
- What does `OVER (PARTITION BY … ORDER BY …)` mean, and what frame do you get if you write none? (not in sources, but standard) — PARTITION BY restarts the calculation for each key and ORDER BY sequences the rows inside it; with an ORDER BY the default frame runs from the start of the partition to the current row, which makes `SUM(amount) OVER (PARTITION BY cust ORDER BY d)` a running total, and without ORDER BY the frame is the entire partition.
- What is the difference between ROWS and RANGE in a window frame? (not in sources, but standard) — ROWS counts physical rows, RANGE counts value peers, so on a day with three orders every one of them gets the end-of-day running total under RANGE; write ROWS unless you specifically want peer semantics.
- What do LAG and LEAD do? (not in sources, but standard) — return a column's value from an earlier or later row of the same partition, which is how you compute month-over-month change, time between events and state transitions without a self-join.
- ★ How do you retrieve alternate (odd or even) records from a table? — number the rows first and filter on the parity of the number: `MOD(ROW_NUMBER() OVER (ORDER BY id), 2) = 0`; the source's `MOD(id,2) = 0` filters on even *ids*, which is the same thing only if the ids are gapless.
- What is the difference between Oracle's ROWNUM and ROW_NUMBER()? — ROWNUM is assigned as rows are produced, before ORDER BY, so `WHERE ROWNUM <= 10 ORDER BY salary DESC` returns ten arbitrary rows sorted; ROW_NUMBER() OVER (ORDER BY …) is assigned after the ordering, which is why the top-N query needs it (or a subquery around the sorted set).
- What is the query to display the nth record from a table? — `ROW_NUMBER() OVER (ORDER BY …) = n`, or `OFFSET n-1 ROWS FETCH NEXT 1 ROW ONLY`; the source's `WHERE id = n` only works if ids are dense and nothing was ever deleted.
- How do you fetch the first and last record, or the first and last row per group? — ORDER BY with LIMIT for the whole table; per group use FIRST_VALUE/LAST_VALUE, or ROW_NUMBER = 1 over ascending and descending orders, and give LAST_VALUE an explicit full frame.
- How do you get the top three marks, and what changes when there are ties? — `SELECT DISTINCT marks … ORDER BY marks DESC LIMIT 3` is fine for one flat list, but `DENSE_RANK() <= 3` keeps every tied student and also works per class.
- ★ You show 10 rows per page and also need the total number of matching rows — how? — add `COUNT(*) OVER ()` to the select list so one pass returns both; MySQL's `SQL_CALC_FOUND_ROWS` / `FOUND_ROWS()` is MySQL-only and deprecated since 8.0.17.
- ★ How does a columnar warehouse optimize aggregations and window functions? — it prunes blocks with zone maps and sort keys and reads fewer bytes thanks to columnar compression, and when the table's sort/distribution key already matches PARTITION BY and ORDER BY the window's sort disappears.
- Why use a window function instead of a self-join or a correlated subquery? — one pass with one sort instead of re-reading the table per row, and the intent (rank, previous value, running total) is stated directly rather than reconstructed from a join predicate.

## Traps
- Filtering on a window function in WHERE or HAVING: it does not exist yet at that point, so wrap it in a CTE or subquery, or use QUALIFY where the engine has it.
- Using ROW_NUMBER when the business means "ties share a rank": ROW_NUMBER picks an arbitrary winner, and a rerun can pick a different one, so always add a deterministic tie-breaker to the ORDER BY.
- LAST_VALUE returning the current row instead of the partition's last row, because the default frame stops at the current row; state `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`.
- Leaving the default RANGE frame when you meant ROWS, so every row sharing a timestamp receives the same end-of-tie running total.
- Reaching for a window where GROUP BY is enough: the result set stays at full detail and each distinct OVER specification adds another sort.
- Expecting a window to see rows that WHERE removed: the window operates on the filtered, grouped result, so a day excluded by the WHERE clause contributes nothing to the running total.

## Graph
- **Needs first:** [[sql-aggregation]]
- **Leads to:** [[sql-query-patterns]]
- **Asked together with:** [[sql-performance-indexing]]

