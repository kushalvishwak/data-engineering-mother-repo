---
id: sql-query-patterns
title: Classic SQL Query Patterns
tier: 0
priority: must-know
sources: [obenner/sql.md, obenner/cdc.md]
---

# Classic SQL Query Patterns

## Say it in one line
Almost every SQL puzzle an interviewer hands you is one of six shapes — rank-and-filter, group-and-having, self-join, anti-join, window frame, or recursive walk — so name the shape first and the query writes itself.

## Must be able to recite
- **Nth highest** — `DENSE_RANK() OVER (ORDER BY salary DESC)` in a subquery, then filter `= n` outside; DENSE_RANK because tied salaries must share one rank.
- **Top-N per group** — `ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC)` in a subquery, then `WHERE rn <= n`, because a window function cannot be filtered in WHERE.
- **Find duplicates** — `GROUP BY <the columns that define a duplicate> HAVING COUNT(*) > 1`; group by every such column, not just one.
- **Delete duplicates, keep one** — number the rows inside each key with `ROW_NUMBER()` and delete where the number is greater than 1.
- **Dedupe to the latest record** — `ROW_NUMBER() OVER (PARTITION BY id ORDER BY updated_at DESC, id DESC) = 1`, always with a deterministic tiebreaker so reruns give the same answer.
- **Running total** — `SUM(amt) OVER (ORDER BY d ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)`; say ROWS explicitly, because the default RANGE frame lumps tied dates together.
- **Group-wise maximum with other columns** — rank inside the group or join the aggregate back; selecting a non-aggregated column beside `MAX()` is invalid (and silently wrong in older MySQL).
- **Anti-join** — `NOT EXISTS`, `LEFT JOIN ... WHERE b.key IS NULL`, or `EXCEPT`/`MINUS`; `NOT IN` breaks the moment the subquery yields a NULL.
- **Islands** — subtract a `ROW_NUMBER()` from the ordered value: the difference is constant within a consecutive run, so `GROUP BY` it to get each island's start and end.
- **Gaps** — `LEAD(d) OVER (ORDER BY d)` and keep the rows where the next value is more than one step ahead; a calendar table plus an anti-join finds missing dates.
- **Pivot** — conditional aggregation, one expression per output column: `SUM(CASE WHEN month = 'Jan' THEN amt END) AS jan`; unpivot with `UNION ALL` or a lateral join.
- **Hierarchy traversal** — a recursive CTE seeded on the root rows, joining each child to the level above, carrying a `level` counter for depth and cycle protection.
- **Pagination** — `LIMIT 25, 100` means skip 25 and take 100 (the standard spelling is `OFFSET 25 ROWS FETCH NEXT 100 ROWS ONLY`); deep offsets get slow, so paginate on the last key seen.
- **Odd, even and alternate rows** — apply `MOD` to a generated row number, never to the id column, because ids have gaps.
- **Date ranges** — `d >= '2024-01-01' AND d < '2025-01-01'` beats `BETWEEN` as soon as the column carries a time component, and it stays index-friendly.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ **Write a query for the second highest salary.** — `SELECT MAX(salary) FROM emp WHERE salary < (SELECT MAX(salary) FROM emp)` is the safe one-liner; the interview-grade answer is `DENSE_RANK() OVER (ORDER BY salary DESC) = 2` in a subquery. *(the source's `WHERE salary NOT IN (SELECT MAX(salary))` works but returns nothing rather than NULL when every salary is equal)*
- ★ **Write a query for the nth highest salary.** — Either the correlated form `WHERE (n-1) = (SELECT COUNT(DISTINCT e2.salary) FROM emp e2 WHERE e2.salary > e1.salary)`, or rank with `DENSE_RANK()` and filter `= n` — the ranking version reads better and scales.
- ★ **Find duplicate rows, or employees with a duplicate email.** — `SELECT email, COUNT(*) FROM employee GROUP BY email HAVING COUNT(*) > 1`; to remove them, number rows per email with `ROW_NUMBER()` and delete where the number exceeds 1. *(the source selects `name` alongside `GROUP BY email`, which is invalid in any engine with strict grouping turned on)*
- ★ **Find the maximum salary per department, including departments with no employees.** — `SELECT d.dept_name, MAX(e.salary) FROM department d LEFT OUTER JOIN employee e ON e.dept_id = d.id GROUP BY d.dept_name`; the LEFT JOIN is the whole trick, and empty departments come back with NULL.
- **Return the employees who earn that departmental maximum, not just the number.** — Rank within the department (`ROW_NUMBER()`/`RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC)`) and keep rank 1, since you cannot select the employee's name next to a bare `MAX()`.
- **Compute a running total of daily sales.** — `SUM(amt) OVER (ORDER BY sale_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)`, partitioning by customer or region when the total should restart. *(not in sources, but standard)*
- **Find consecutive runs, or the gaps in a sequence of dates.** — Islands: group by `date - ROW_NUMBER() OVER (ORDER BY date)`, which is constant inside a run; gaps: compare each row with `LEAD()` and keep the ones where the next value skips ahead. *(not in sources, but standard)*
- **Turn twelve months of rows into twelve columns.** — Conditional aggregation, one `SUM(CASE WHEN month = 'Jan' THEN amt END)` per column with `GROUP BY` on the row key; SQL Server and Oracle also have a `PIVOT` operator, and reversing it needs `UNPIVOT` or `UNION ALL`. *(not in sources, but standard)*
- **Given a stream of change records, build the current state per key.** — Keep the append-only log, then `ROW_NUMBER() OVER (PARTITION BY primary_key ORDER BY commit_lsn DESC, updated_at DESC) = 1`; the deterministic ordering is what makes reruns idempotent.
- ★ **Find rows in table A that are not in table B without using NOT IN.** — `SELECT * FROM a EXCEPT SELECT * FROM b` (`MINUS` in Oracle), or `NOT EXISTS`, or `LEFT JOIN b ON ... WHERE b.key IS NULL`.
- ★ **What does `SELECT CASE WHEN null = null THEN 'True' ELSE 'False' END` return?** — 'False', because NULL is never equal to anything, including another NULL; the only test is `IS NULL`.
- **Write a query to walk a manager hierarchy.** — Recursive CTE: anchor on `manager_id IS NULL`, `UNION ALL` the join of employees to the previous level, and select the accumulated level or path.
- ★ **Find employees who share both a name and an email.** — `GROUP BY name, email HAVING COUNT(*) > 1` — group by both columns, not one.
- ★ **Get the three highest marks.** — `SELECT DISTINCT marks FROM student ORDER BY marks DESC LIMIT 3`; use `DENSE_RANK() <= 3` when ties should all be returned.
- **Fetch the first and the last record of a table.** — There is no first or last without an ORDER BY: `ORDER BY id LIMIT 1` and `ORDER BY id DESC LIMIT 1`. *(the source answers "`WHERE id = 1`" for the first record, which only works if that id happens to exist)*
- **Display the first 4 and the last 3 records.** — `ORDER BY id LIMIT 4`, and `ORDER BY id DESC LIMIT 3` (re-sort in an outer query if you need them ascending).
- **Fetch the nth record of a table.** — `ORDER BY id LIMIT 1 OFFSET n-1`, or `ROW_NUMBER()` filtered `= n`.
- ★ **Display the odd-numbered and even-numbered rows.** — `MOD(ROW_NUMBER() OVER (ORDER BY id), 2) = 1` for odd and `= 0` for even. *(the sources use `MOD(id, 2)`, which only matches row positions if the ids are gapless — it answers a different question)*
- **Retrieve alternate records in Oracle.** — Generate the numbering first, then filter: `SELECT * FROM (SELECT ROW_NUMBER() OVER (ORDER BY id) rn, e.* FROM emp e) WHERE MOD(rn,2) = 0`; `ROWNUM` is assigned before ORDER BY, so it must be wrapped.
- **Find 10 employees whose id is an odd number.** — `SELECT * FROM emp WHERE MOD(id, 2) = 1 FETCH FIRST 10 ROWS ONLY` in Oracle, `LIMIT 10` in MySQL/Postgres, `SELECT TOP 10` in SQL Server. *(the source calls `TOP` and `%` Oracle syntax — they are SQL Server's; Oracle uses `ROWNUM`/`FETCH FIRST` and `MOD()`)*
- **Return 100 books starting from the 25th.** — `SELECT title FROM books ORDER BY id LIMIT 25, 100` — first number is the offset, second is the count; use `OFFSET ... FETCH NEXT` for the portable spelling.
- **Page 10 results at a time while showing the total number of matches.** — Add `COUNT(*) OVER ()` to the paged query, or run a separate `COUNT(*)`. *(the source's `SQL_CALC_FOUND_ROWS` with `FOUND_ROWS()` is deprecated as of MySQL 8.0.17 and should not be your answer)*
- **List employees whose date of birth falls between two dates.** — `WHERE birth_date >= DATE '1990-01-01' AND birth_date < DATE '2001-01-01'`; `BETWEEN` is inclusive on both ends and silently drops the final day once a time component exists.
- **Get the quarter from a date.** — `EXTRACT(QUARTER FROM d)` or `QUARTER(d)` in MySQL; the source's `TO_CHAR(d, 'Q')` is the Oracle spelling.
- **Find every employee whose name contains "rich" in any case.** — `WHERE UPPER(emp_name) LIKE '%RICH%'`, or a case-insensitive collation; note that both the function and the leading wildcard rule out an index seek.
- **Select all records whose name is one of a list.** — `WHERE name IN ('a','b')` — the same shape as "teams that won 2, 4, 6 or 8 games".
- **Select all users whose phone number is NULL.** — `WHERE phone_number IS NULL`. *(the source's `ISNULL(col)` is MySQL-only, and in SQL Server `ISNULL(a,b)` means something else entirely — a two-argument COALESCE)*
- **Return distinct values, and count them.** — `SELECT DISTINCT col FROM t` and `SELECT COUNT(DISTINCT col) FROM t`.
- **How do you replace a NULL in the output?** — `COALESCE(col, 'n/a')` is the portable form; `IFNULL` is MySQL, `NVL` is Oracle, `ISNULL` is SQL Server.
- **How many days are there between two dates?** — `DATEDIFF(d2, d1)` in MySQL, `d2 - d1` in PostgreSQL and Oracle, `DATEDIFF(day, d1, d2)` in SQL Server.
- **How do you write if/else logic in SQL?** — `CASE WHEN ... THEN ... ELSE ... END`, which is standard; Oracle's `DECODE` does the simple equality case only.
- **How do you get the number of rows a statement affected?** — The client's row count (`@@ROWCOUNT`, `ROW_COUNT()`, `cursor.rowcount`), not a `COUNT(*)` — which counts rows, and counts only non-NULL values when you pass it a column.
- **Which auto-increment value did the last insert get?** — `LAST_INSERT_ID()` in MySQL, `SCOPE_IDENTITY()` in SQL Server, `RETURNING id` in PostgreSQL — all scoped to your own session, so concurrent inserts cannot leak in.
- **Is it safe to use ROWID to locate a row, and what is a pseudo-column?** — Only inside one transaction: a pseudo-column such as `ROWID` or `ROWNUM` is readable but not stored, and a row's ROWID changes on a table rebuild and can be reused after a delete, so never persist it.
- **How do you pick a random sample of rows?** — `ORDER BY RAND()` (or `RANDOM()`) works for small tables but sorts the whole set, so on large tables use a `TABLESAMPLE`/`SAMPLE` clause or filter on a hash of the key.

## Traps
- Answering "second highest" with `LIMIT 1,1` or `salary <> MAX(salary)` — both collapse on tied top salaries, and neither returns NULL when the row does not exist, which is what the graders check.
- Using `MOD(id, 2)` for odd or even *rows* — ids have gaps, so you must number the rows first.
- Quoting `SELECT TOP` or `%` as Oracle syntax, or `ROWNUM` as if it applied after `ORDER BY` — rank in a subquery, then filter outside.
- Filtering a window function in `WHERE` or `HAVING` — it is evaluated after both, so wrap it in a subquery or use `QUALIFY` where the engine supports it.
- `BETWEEN` on a timestamp column — `BETWEEN '2024-01-01' AND '2024-01-31'` loses everything after midnight on the 31st.
- `CREATE TABLE new AS SELECT * FROM old` when you were asked for the same *structure* — it copies the data and none of the indexes, keys or constraints; use `CREATE TABLE new LIKE old` or `WHERE 1=0`.

## Graph
- **Needs first:** [[sql-window-functions]], [[sql-ctes-subqueries]]
- **Leads to:** [[system-design-scenarios]]
- **Asked together with:** [[dsa-coding]]
