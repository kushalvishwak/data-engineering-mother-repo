---
id: sql-joins-sets
title: Joins, Semi/Anti Joins and Set Operations
tier: 0
priority: must-know
sources: [obenner/sql.md, obenner/dwha.md, obenner/data-modeling.md, obenner/cost-optimization.md, cookbook, devinterview]
---

# Joins, Semi/Anti Joins and Set Operations

## Say it in one line
A join matches rows from two inputs on a predicate and can shrink or multiply the row count in the process, while a set operator stacks two result sets of identical shape and removes duplicates unless you write ALL.

## Must be able to recite
- **INNER JOIN** — returns only the rows that satisfy the predicate, so unmatched rows on either side disappear without warning.
- **LEFT OUTER JOIN** — every row of the left input plus its matches, NULL-extended where the right side had none; RIGHT is the same operator with the inputs swapped, which is why most teams only ever write LEFT.
- **FULL OUTER JOIN** — every row of both inputs, NULL-extended on whichever side is missing; MySQL has no FULL OUTER JOIN, so you emulate it with LEFT UNION RIGHT.
- **CROSS JOIN** — every row against every row, N×M rows; omitting or mistyping the ON clause produces the same thing by accident.
- **Self-join** — one table joined to itself under two aliases, used for manager/employee hierarchies and for comparing rows to other rows in the same table.
- **Semi-join (`EXISTS` / `IN`)** — keeps a left row when at least one match exists and never duplicates it, which is the guarantee a plain join cannot give you.
- **Anti-join (`NOT EXISTS`, `LEFT JOIN … WHERE right IS NULL`, `EXCEPT`)** — keeps left rows with no match; `NOT IN` is the one variant that breaks on NULL.
- **Fan-out** — joining to a table that has several matching rows multiplies the left row, so every SUM and COUNT downstream is inflated.
- **ON vs WHERE on an outer join** — a predicate on the optional table placed in WHERE is applied after NULL-extension and silently converts the outer join into an inner join.
- **Equi-join vs theta join** — ON is any predicate, not just equality, so range joins (`event_ts BETWEEN valid_from AND valid_to`) are how you join a fact to an SCD-2 dimension.
- **NULL join keys** — NULL never matches NULL in an ON clause, so rows with NULL keys are dropped by every join type on that side.
- **UNION vs UNION ALL** — UNION removes duplicate rows even if you never write DISTINCT, UNION ALL concatenates and skips that sort or hash, so UNION ALL is the default for disjoint branches.
- **INTERSECT / EXCEPT** — rows present in both, and rows in the first but not the second, both de-duplicated; they treat two NULLs as the same value (unlike `=`), Oracle spells EXCEPT as MINUS, and MySQL only added both in 8.0.31.
- **Set-operator rules** — branches need the same number of columns in compatible types matched by position, output names come from the first branch, and one ORDER BY at the end applies to the whole result.
- **Physical join strategies** — nested loop, hash join and sort-merge; distributed engines add broadcast (ship the small side everywhere) versus shuffle (repartition both sides by the key).

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ What is a join, and what are the different types? — an operation that combines rows from two or more tables on a matching condition; INNER, LEFT/RIGHT/FULL OUTER and CROSS are the syntactic types, and a self-join is a usage pattern rather than a separate type.
- ★ What is the difference between an INNER JOIN and an OUTER JOIN? — INNER keeps only matched pairs, OUTER additionally keeps unmatched rows from one side (LEFT/RIGHT) or both (FULL) with NULLs on the missing side; the source's Venn diagram explains matching but hides fan-out, because a join can return more rows than either input.
- ★ What is the difference between a LEFT OUTER and a RIGHT OUTER JOIN? — which side is preserved: LEFT keeps all rows of the first table, RIGHT keeps all rows of the second, and they are interchangeable by swapping the tables.
- ★ What is a Cartesian or CROSS join, and how do you get one by accident? — every row of one input paired with every row of the other; you produce one by writing `FROM a, b` with no join predicate, by joining on a non-selective column, or by joining a table to itself with no condition.
- Are the resulting relations of a product and a join the same? — no: the product concatenates every row of one relation with every row of the other, the join keeps only the related rows, so an inner join is the product with the ON predicate applied.
- ★ Write a query for the maximum salary and department name for each department. — LEFT OUTER JOIN from department to employee and GROUP BY the department name, so departments with no employees still appear with a NULL maximum; the interviewer is checking whether you ask about empty departments.
- ★ Find the records in table A that are not in table B without using NOT IN. — `SELECT * FROM A EXCEPT SELECT * FROM B` (Oracle MINUS), or `NOT EXISTS`, or `LEFT JOIN B ON … WHERE B.key IS NULL`; EXCEPT compares whole rows and de-duplicates, the other two do not.
- ★ What is UNION, and does it remove duplicates? — it combines multiple query results of the same structure into one; it removes duplicate rows by default even without writing DISTINCT, whereas UNION ALL keeps them.
- When would you use UNION ALL instead of UNION? — whenever the branches cannot overlap or duplicates are meaningful, because it avoids a sort or hash over the combined result.
- What are the rules for a UNION? — equal column counts, compatible data types matched by position rather than by name, output column names taken from the first SELECT, and a single ORDER BY at the very end.
- What are INTERSECT and EXCEPT/MINUS? — the rows common to both queries and the rows in the first that are absent from the second, both de-duplicated; INTERSECT binds tighter than UNION and EXCEPT in standard SQL, so parenthesize when you mix them.
- ★ Find the employees that have the same name and email, or a duplicate email. — `GROUP BY name, email HAVING COUNT(*) > 1` for a duplicate report, or a self-join `a.email = b.email AND a.id <> b.id` when you need the pairs themselves; group by every column of the intended key, not just one.
- What is a self-join and when do you need one? (not in sources, but standard) — the same table aliased twice, used for parent/child hierarchies, for finding pairs of rows inside one table, and historically for previous-row comparisons that window functions now do better.
- What is the difference between putting a condition in ON versus in WHERE on an outer join? (not in sources, but standard) — in ON it is part of the match and unmatched left rows survive as NULL-extended; in WHERE it is applied afterwards and removes those NULL rows, quietly turning the LEFT JOIN into an inner join.
- MySQL has no FULL OUTER JOIN — how do you write one? (not in sources, but standard) — `LEFT JOIN` UNION `RIGHT JOIN` over the same predicate, using UNION rather than UNION ALL so the matched rows are not emitted twice.
- ★ How do you prevent double counting in an analytical model? — enforce the correct grain, join many-to-one only, insert a bridge table for a genuine many-to-many, then define each metric (sum vs distinct count vs last value) and reconcile it against the source.
- How do you validate a model after a change so join duplication does not slip through? — row-count and key-uniqueness checks at each layer, totals reconciled against the source system, drill-through on known entities, and regression tests on the headline metrics.
- ★ How do you optimize a join over large tables? — filter and project down before joining, keep join keys clean and well distributed, choose broadcast for a small side instead of shuffling both, and pre-join into a curated table when the same join repeats in many queries.
- ★ Why does a heavily normalized schema hurt read performance, and what do you do about it? — every additional table is another join, so reporting models denormalize (star schema, wide tables) and accept redundancy and heavier writes in exchange for fewer joins.
- What is an outer join used for in practice? — reporting on the preserved side whether or not a match exists: customers with no orders, departments with no employees, days with no sales.
- What is the difference between an anti-join and simply filtering? — an anti-join answers "no matching row exists at all", which needs `NOT EXISTS`/`IS NULL` on the join key; a WHERE filter on the joined table only inspects rows that did match.

## Traps
- Adding DISTINCT to make duplicate rows go away: it hides a fan-out rather than fixing it, and it silently changes every COUNT and SUM. Find the join that multiplied the rows.
- Filtering the optional side of a LEFT JOIN in WHERE (`WHERE o.status = 'PAID'`), which removes exactly the unmatched rows you outer-joined to keep; move the predicate into ON.
- `NOT IN (SELECT col FROM …)` where the column is nullable — a single NULL makes the whole result empty; use `NOT EXISTS`.
- Calling a join one-to-many without checking: run `GROUP BY key HAVING COUNT(*) > 1` on both sides first, because a duplicate key on the "one" side turns it into many-to-many.
- Reaching for UNION by habit: the implicit de-duplication is a full sort or hash over both branches, and it also conceals the fact that you were generating duplicates.
- Expecting rows with NULL join keys to match each other, or to survive an inner join at all; handle them explicitly with COALESCE to a sentinel or a separate branch.

## Graph
- **Needs first:** [[sql-semantics]]
- **Leads to:** [[sql-aggregation]], [[sql-query-patterns]]
- **Asked together with:** [[relational-modeling]]

