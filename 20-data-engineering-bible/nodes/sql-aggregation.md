---
id: sql-aggregation
title: Aggregation, GROUP BY and Grouping Sets
tier: 0
priority: must-know
sources: [obenner/sql.md, obenner/dwha.md, obenner/data-modeling.md]
---

# Aggregation, GROUP BY and Grouping Sets

## Say it in one line
Aggregation collapses many rows into one row per group: GROUP BY names the group, the aggregate functions summarize each group and skip NULLs, and HAVING filters the groups once they exist.

## Must be able to recite
- **Aggregate function** — reduces a set of rows to a single value per group, and with no GROUP BY the entire result set is one group.
- **GROUP BY** — defines the grouping keys, and every non-aggregated column in the SELECT list must appear in it (MySQL only began enforcing this by default in 5.7 with ONLY_FULL_GROUP_BY).
- **Evaluation order** — WHERE filters rows, GROUP BY forms groups, the aggregates compute, HAVING filters groups, then SELECT and ORDER BY run; that order is why an aggregate cannot appear in WHERE.
- **HAVING vs WHERE** — WHERE is a row predicate applied before grouping, HAVING is a group predicate applied after it and is the only one that may contain an aggregate.
- **COUNT(\*) vs COUNT(col) vs COUNT(DISTINCT col)** — rows, non-NULL values of that column, and distinct non-NULL values of that column.
- **NULL and empty groups** — every aggregate except COUNT(\*) ignores NULLs, so AVG divides by the non-NULL count; over zero rows COUNT returns 0 while SUM, AVG, MIN and MAX return NULL.
- **GROUP BY and NULL** — all NULLs collapse into a single group, unlike `=`, which never matches NULL.
- **DISTINCT vs GROUP BY** — identical de-duplication and similar cost; use GROUP BY when you also need an aggregate, DISTINCT when you only need unique rows.
- **Conditional aggregation** — `SUM(CASE WHEN … THEN 1 ELSE 0 END)`, or the ANSI `COUNT(*) FILTER (WHERE …)`, is the portable way to count a subset or pivot rows into columns.
- **ROLLUP(a, b, c)** — hierarchical subtotals following that column order plus a grand total, so n columns produce n+1 grouping levels.
- **CUBE(a, b, c)** — every combination of the listed columns, 2^n grouping levels, which is how a cube-style report gets built in one pass.
- **GROUPING SETS** — you list exactly the grouping levels you want; ROLLUP and CUBE are shorthands for particular sets.
- **GROUPING(col)** — returns 1 when that column was rolled up in the row, which is how you tell a subtotal row from a genuine NULL.
- **Additivity** — counts and amounts are additive, ratios and percentages are not, so store numerator and denominator and divide only after summing.
- **Aggregate table** — a pre-computed summary of the fact table at a coarser grain, trading storage and freshness for query latency.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ What is the difference between the WHERE clause and the HAVING clause? — WHERE filters individual rows before grouping and cannot contain an aggregate, HAVING filters the groups afterwards, so `COUNT(*) > 10` belongs in HAVING.
- ★ What are the aggregate functions in SQL? — COUNT, SUM, AVG, MIN and MAX, plus STDDEV/VARIANCE and the percentile functions; ROUND, which the source lists as an aggregate, is a scalar function and does not group anything.
- ★ Write a query to find the maximum salary in each department. — `SELECT dept_id, MAX(salary) FROM employee GROUP BY dept_id`; to show the department name, join the department table and group by the name, using a LEFT JOIN if empty departments must still appear.
- ★ Write a query to find duplicate rows, or employees with a duplicate email. — `GROUP BY email HAVING COUNT(*) > 1`; group by every column that makes up the intended key, otherwise you report the wrong rows.
- ★ How do you count the rows a query returns, and how is COUNT(col) different? — COUNT(\*) counts rows, COUNT(col) counts only rows where that column is not NULL, and COUNT(DISTINCT col) de-duplicates first.
- ★ If the value in a column repeats, how do you get the unique values and how many there are? — `DISTINCT col` or `GROUP BY col`, and `COUNT(DISTINCT col)` for the number.
- Can you use an aggregate function in a WHERE clause? — no, because WHERE is evaluated before the groups exist; move the condition to HAVING, or compute the aggregate in a subquery, a CTE or a window function.
- What does GROUP BY do with NULLs? (not in sources, but standard) — they form one group of their own, so a NULL dimension key shows up as a visible bucket rather than being dropped.
- ★ Get the second highest salary without using window functions. — `SELECT MAX(salary) FROM employee WHERE salary < (SELECT MAX(salary) FROM employee)`; the source's `NOT IN (SELECT MAX(salary) …)` variant works too but returns NULL when every salary is identical.
- Write a query for the number of employees per department, showing only departments with more than ten. — `SELECT dept_id, COUNT(*) FROM employee GROUP BY dept_id HAVING COUNT(*) > 10`, remembering that COUNT counts rows, so an earlier fan-out inflates it.
- Why is a filter in the WHERE clause cheaper than filtering after the grouping? — rows removed by WHERE are never grouped, sorted or aggregated, so both CPU and any spill to disk shrink.
- How do you produce subtotals and a grand total in a single query? (not in sources, but standard) — `GROUP BY ROLLUP(region, city)` for a hierarchy, CUBE for every combination, GROUPING SETS for a named list, and `GROUPING(col)` to distinguish subtotal rows from real NULLs.
- How do you count only the rows meeting a condition, or pivot rows into columns? (not in sources, but standard) — conditional aggregation: one `SUM(CASE WHEN status = 'PAID' THEN amount ELSE 0 END)` per output column, or `COUNT(*) FILTER (WHERE …)` where it is supported.
- ★ What is an aggregate table and why would you build one? — a summary of warehouse data grouped to coarser levels of the dimensions, so reports do not scan millions of detail rows; the cost is another object to refresh, reconcile and keep consistent with the detail.
- What is the grain of a fact table, and why does it decide your aggregation? — the grain is what exactly one row represents, and SUM is only meaningful at or above that grain, which makes it the first question to settle in any model.
- What are non-additive facts? — measures such as ratios, percentages and balances that cannot be summed across a dimension; recompute them from summed components, or use a semi-additive rule such as last value.
- How do you avoid double counting when you aggregate across a join? — aggregate to the right grain before joining, keep joins many-to-one, and use a bridge table for a real many-to-many rather than joining the two many-sides directly.
- ★ You return 10 rows per page but also need the total number of matching rows — how? — add `COUNT(*) OVER ()` to the same query, or run a separate `COUNT(*)`; MySQL's `SQL_CALC_FOUND_ROWS` is deprecated as of 8.0.17.
- How do you get the three highest marks from a table? — `SELECT DISTINCT marks FROM student ORDER BY marks DESC LIMIT 3` for a single list; if ties must all be kept, or you need it per class, use `DENSE_RANK() <= 3`.
- What is the difference between DISTINCT and GROUP BY for de-duplication? — none in the result when no aggregate is involved, and both cost a sort or hash; GROUP BY is the form you extend once you need an aggregate.
- Why do OLAP systems pre-aggregate instead of computing on the fly? — sub-second answers need the combinations of dimension granularities materialized in advance, which is the same idea as an aggregate table or a materialized view in SQL.
- What role do bitmap indexes play in aggregation? — on low-cardinality dimension columns the engine combines bitmaps with AND/OR before touching any rows, which suits read-mostly warehouses and not write-heavy OLTP tables.

## Traps
- Putting an aggregate in WHERE (`WHERE COUNT(*) > 10`); it must be HAVING, or a subquery if you also need to filter rows.
- Writing `COUNT(col)` when you meant rows: on a nullable column the report quietly under-counts, and nobody notices until reconciliation.
- Averaging an average: AVG over already-grouped rows is not the overall average — sum the numerator and the denominator, then divide once.
- SUM after a fan-out join, which returns a clean-looking multiple of the truth; compare the row count before and after the join.
- HAVING with no GROUP BY treats the whole result as one group, so `HAVING COUNT(*) > 1` returns either every row or none.
- Selecting a column that is not in the GROUP BY on MySQL without ONLY_FULL_GROUP_BY: you get an arbitrary row's value, which looks correct on test data and is wrong in production.

## Graph
- **Needs first:** [[sql-semantics]]
- **Leads to:** [[sql-window-functions]]
- **Asked together with:** [[dimensional-modeling]]

