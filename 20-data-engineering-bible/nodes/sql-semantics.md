---
id: sql-semantics
title: SQL Semantics — Execution Order, NULLs, Types
tier: 0
priority: must-know
sources: [obenner/sql.md]
---

# SQL Semantics — Execution Order, NULLs, Types

## Say it in one line
SQL is a declarative, set-based language where you state the result you want and the engine picks the plan, so almost every surprise in a query traces back to one of two things: the logical order in which the clauses are evaluated, or the fact that NULL means unknown.

## Must be able to recite
- **Logical execution order** — FROM/JOIN → WHERE → GROUP BY → HAVING → window functions → SELECT/DISTINCT → ORDER BY → LIMIT, which is not the order you write it in.
- **Why a SELECT alias fails in WHERE** — WHERE is evaluated before the SELECT list, so the alias does not exist yet; ORDER BY runs after it, so there the alias works.
- **NULL** — a marker for unknown, not zero and not an empty string, and any arithmetic or comparison touching it yields NULL/UNKNOWN, so `IS NULL` is the only valid test.
- **Three-valued logic** — a predicate returns TRUE, FALSE or UNKNOWN, and WHERE and ON keep only TRUE, so UNKNOWN rows disappear exactly like FALSE ones.
- **COALESCE(a, b, …)** — returns the first non-NULL argument and is the portable form; IFNULL is MySQL's two-argument version, NVL is Oracle's.
- **NULLIF(a, b)** — returns NULL when the two are equal, which is the standard trick for turning a zero denominator into NULL instead of an error.
- **CASE** — the only ANSI if/else, in searched form (`CASE WHEN cond THEN …`) or simple form (`CASE col WHEN val THEN …`), evaluated top-down and stopping at the first match.
- **DISTINCT** — de-duplicates the whole projected row, not the single column it sits next to, and costs a sort or a hash.
- **CAST(x AS type)** — explicit conversion; an implicit conversion on a column (string column compared to a number) blocks index use and can silently change collation.
- **DECIMAL vs FLOAT/DOUBLE** — DECIMAL is exact with a fixed scale, FLOAT and DOUBLE are binary approximations, so money and quantities are always DECIMAL.
- **CHAR vs VARCHAR** — CHAR is fixed length and blank-padded, VARCHAR stores only what you put in plus a length prefix.
- **DATE vs TIMESTAMP** — DATE is a calendar day, TIMESTAMP is an instant on the clock; store UTC and convert at the reporting edge.
- **Collation** — the rule set for comparing and sorting text, so it decides case- and accent-sensitivity, and two columns with different collations can fail to compare at all.
- **LIKE** — `%` matches any number of characters and `_` exactly one, and a leading `%` forces a scan because no index can seek to it.
- **BETWEEN** — inclusive at both ends, which makes it wrong on a TIMESTAMP column unless you switch to `>= start AND < end`.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ What is the result of `SELECT CASE WHEN null = null THEN 'True' ELSE 'False' END`? — 'False', because `null = null` is UNKNOWN rather than TRUE, so the ELSE branch runs; `CASE WHEN null IS NULL` is the version that returns 'True'.
- In what order does the engine logically evaluate a SELECT? (not in sources, but standard) — FROM/JOIN, WHERE, GROUP BY, HAVING, window functions, SELECT/DISTINCT, ORDER BY, LIMIT; every "why can't I use that here" question falls out of this list.
- Why can you reference a SELECT alias in ORDER BY but not in WHERE? (not in sources, but standard) — WHERE runs before the SELECT list is projected, ORDER BY runs after it, so only ORDER BY can see the alias.
- What are the three truth values in SQL, and what happens to a row whose predicate is UNKNOWN? (not in sources, but standard) — TRUE, FALSE and UNKNOWN; the row is dropped as if the predicate were FALSE, and `NOT UNKNOWN` is still UNKNOWN.
- ★ What is a NULL value? — a field with no value, which is different from 0 and from a string of spaces; it means "unknown", so two NULLs are not equal to each other.
- How would you select all users whose phone number is NULL? — `WHERE phone IS NULL`; MySQL's `ISNULL(phone)` in the source works but is not portable.
- ★ What is the use of the IFNULL / NVL function? — it substitutes a value when the argument is NULL (the source's "converts the null value to its actual value" is garbled — it replaces NULL with a fallback), and COALESCE is the portable equivalent.
- What is the feature in SQL for writing if/else statements? — CASE, in searched or simple form; Oracle's DECODE only does the simple form, so name CASE first.
- ★ If the values in a column repeat, how do you find the unique values and count them? — `SELECT DISTINCT col`, and `COUNT(DISTINCT col)` for the number, which ignores NULLs.
- How does the engine execute DISTINCT? — it is equivalent to grouping on every selected column, so it needs a sort or hash, and combined with ORDER BY it usually needs a temporary table.
- Why is a WHERE-clause filter faster than filtering the data afterwards? — the condition is applied while rows are being read, so eliminated rows never reach the grouping, sorting or formatting stages.
- ★ How do you show only the top 10 rows, or 100 rows starting from the 25th? — `LIMIT 100 OFFSET 25` (MySQL's `LIMIT 25,100`), ANSI `OFFSET 25 ROWS FETCH NEXT 100 ROWS ONLY`, SQL Server `TOP`, Oracle `FETCH FIRST` (older Oracle code filters ROWNUM).
- ★ You show 10 search results per page but also need the total count — how? — `COUNT(*) OVER ()` alongside the page, or a second `COUNT(*)` query; the source's `SQL_CALC_FOUND_ROWS` + `FOUND_ROWS()` is MySQL-only and deprecated since MySQL 8.0.17.
- Find all employees whose name contains "rich" regardless of case. — `WHERE UPPER(name) LIKE '%RICH%'` (Postgres `ILIKE`), accepting that wrapping the column in a function rules out an index seek.
- How do you use LIKE, and what do `%` and `_` mean? — `%` matches zero or more characters, `_` matches exactly one, and `ESCAPE` lets you search for a literal `%` or `_`.
- ★ How do you write "column is one of these values"? — `WHERE name IN ('a','b')`, which is shorthand for OR'd equality; the NOT IN form is unsafe as soon as the list can contain NULL.
- Get the employees whose date of birth is between 01/01/1990 and 31/12/2000. — `WHERE dob BETWEEN DATE '1990-01-01' AND DATE '2000-12-31'`; BETWEEN includes both endpoints, and write ISO literals instead of the source's locale-dependent '31/12/2000'.
- ★ What string functions do you know? — LENGTH/CHAR_LENGTH, UPPER/LOWER, SUBSTRING, TRIM/LTRIM/RTRIM, CONCAT (or `||`), REPLACE, and POSITION/INSTR.
- What is the difference between LENGTH and CHAR_LENGTH? — LENGTH counts bytes, CHAR_LENGTH counts characters; identical for ASCII, different for UTF-8 text.
- What is the difference between SUBSTR and INSTR? — SUBSTR returns a slice given a start position and length, INSTR returns the position at which a search string occurs.
- How do you concatenate two strings? — `CONCAT(a, b)` or the ANSI `a || b`; in standard SQL concatenating a NULL produces NULL, while Oracle treats it as an empty string.
- ★ How do you calculate the number of days between two dates? — subtract the dates (`d2 - d1` in Postgres and Oracle) or use DATEDIFF; MySQL is `DATEDIFF(end, start)` and SQL Server is `DATEDIFF(unit, start, end)`, so the signature is not portable.
- ★ How do you get the quarter, or the month, out of a date? — `EXTRACT(QUARTER FROM d)` and `EXTRACT(MONTH FROM d)`; the source's `TO_CHAR(d,'Q')` and `MONTH(d)` are the Oracle and MySQL spellings.
- How do you add three minutes to a date? — `ts + INTERVAL '3' MINUTE`, or MySQL's `ADDDATE(ts, INTERVAL 3 MINUTE)`; never add a bare number to a timestamp.
- How do you get the current date and time? — `CURRENT_DATE` and `CURRENT_TIMESTAMP` (MySQL `NOW()`); say which time zone and whether the value is fixed for the whole transaction.
- How do you offload date formatting to the database? — `DATE_FORMAT(ts, '%Y-%m-%d')` or `TO_CHAR`, but keep the stored column a real date type and format only at the presentation layer.
- ★ How is a Unix timestamp different from a database TIMESTAMP, and how do you convert between them? — the Unix value is an integer count of seconds since 1970-01-01 UTC while the database type renders an instant as `YYYY-MM-DD HH:MM:SS`, and `UNIX_TIMESTAMP()`/`FROM_UNIXTIME()` convert (the source's "32-bit" is dated, since 32-bit seconds overflow in 2038 and current systems store 64-bit).
- ★ What groups of data types does SQL have? — character/string, exact numeric (INT, DECIMAL), approximate numeric (FLOAT, DOUBLE), date-time (DATE, TIME, TIMESTAMP), boolean/bit and binary/large object, plus JSON and array types in modern engines.
- ★ What is the difference between CHAR and VARCHAR? — CHAR is fixed length and blank-padded, VARCHAR is variable length with a length prefix; the source's size limits are engine-specific (MySQL VARCHAR runs to the 65,535-byte row limit, the 4000 figure is Oracle's VARCHAR2) and its "CHAR is 50% faster" claim is not a real measurement.
- How do you convert a numeric value to a character string? — `CAST(value AS CHAR)` or `CAST(value AS VARCHAR(n))`; prefer explicit CAST over letting the engine convert implicitly.
- What is the difference between FLOAT, DOUBLE and REAL, and which type holds money? — 4-byte and 8-byte binary approximations with REAL as a synonym, so money and rates go in DECIMAL/NUMERIC.
- How do you enter boolean values, and what is the difference between BOOL, TINYINT and BIT? — write TRUE/FALSE; in MySQL BOOL is an alias for TINYINT(1) while BIT stores raw bits, so the "boolean" column is really a small integer.
- What is collation? — the set of rules for comparing and sorting character data, which fixes case-sensitivity, accent-sensitivity and sort order; mixing collations in a comparison raises an error in MySQL.
- Why do we use escape characters in SQL queries? — quotes, backslashes and the LIKE wildcards are reserved, so they must be escaped to be read as data; for user input the real answer is parameter binding, not hand-escaping.
- What is the difference between RENAME and an alias? — RENAME permanently changes the name of the object, an alias is a temporary name that exists only for that statement.
- How do you get the number of rows a query returns? — `SELECT COUNT(*)`; `COUNT(col)` counts only rows where that column is not NULL, which is a different number.

## Traps
- Writing `col = NULL` or `col <> NULL`: it is not a syntax error, it just returns nothing — use `IS NULL` / `IS NOT NULL`.
- `col NOT IN (subquery)` returns an empty result if the subquery produces a single NULL; rewrite as `NOT EXISTS`, or filter the NULLs out first.
- Wrapping the filtered column in a function — `UPPER(col)`, `DATE(ts)`, `CAST(col AS …)` — makes the predicate non-sargable; transform the literal side instead, or add a functional index.
- Assuming rows come back in insert or index order: without ORDER BY there is no order at all, so `LIMIT` without ORDER BY is a non-deterministic answer.
- Using FLOAT for amounts and then failing reconciliation by a few paise; use DECIMAL(18,2) or integer minor units.
- `BETWEEN '2024-01-01' AND '2024-01-31'` on a TIMESTAMP column silently drops everything after midnight on the 31st; use `>= '2024-01-01' AND < '2024-02-01'`.

## Graph
- **Needs first:** —
- **Leads to:** [[sql-joins-sets]], [[sql-aggregation]]
- **Asked together with:** [[sql-ddl-dml-transactions]]

