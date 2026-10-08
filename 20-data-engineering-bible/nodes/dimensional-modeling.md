---
id: dimensional-modeling
title: Dimensional Modelling
tier: 0
priority: must-know
sources: [obenner/dwha, obenner/data-modeling, devinterview, cookbook]
---

# Dimensional Modelling

## Say it in one line
Dimensional modelling organises analytical data as numeric facts recorded at one declared grain, surrounded by denormalised descriptive dimensions, so a business user can slice a measure without writing a complicated join.

## Must be able to recite
- **Grain** — the sentence "one row per ___" that you declare before writing any DDL; if you cannot say it, every aggregate will silently double count and no key is trustworthy.
- **Fact table** — one row per business event at the declared grain, holding numeric measures plus foreign keys to dimensions; narrow, very long, and it is the table that grows.
- **Dimension table** — the descriptive context (who, what, where, when) used to filter, group and label; wide, short, and deliberately denormalised so users get their attributes in one hop.
- **Star schema** — one fact table joined directly to one flat table per dimension, so every join is fact-to-dimension many-to-one and exactly one hop; that is why queries are fast and BI tools can generate the SQL themselves.
- **Snowflake schema** — a star whose dimensions have been normalised into parent tables (`dim_product → product_category → product_manufacturer`), so reaching an attribute takes two or more hops; it removes redundancy and gives one place to maintain a hierarchy, at the cost of more joins, slower queries and tools/users that get lost.
- **Galaxy schema (fact constellation)** — several fact tables that *share the same conformed dimensions*, e.g. a sales fact and a returns fact both joined to `dim_date`, `dim_product`, `dim_customer`; this is what a real enterprise warehouse looks like, and sharing the dimensions is the defining property, not merely having many tables.
- **When snowflake actually wins** — huge dimensions where the duplicated text is genuinely expensive, deep hierarchies that must be maintained in exactly one place, attributes shared by several dimensions (outriggers), or a load window too tight to flatten an already-normalised source; otherwise default to star.
- **Three fact types** — transaction (one row per event, fully additive), periodic snapshot (one row per entity per period, e.g. daily account balance), accumulating snapshot (one row per process instance, updated in place as milestones complete, carrying several date keys and lag measures).
- **Additive, semi-additive, non-additive** — additive sums across every dimension (sales amount); semi-additive sums across all dimensions except time (account balance, stock on hand — sum across accounts, never across days, take the last value or an average); non-additive cannot be summed at all (ratios, percentages, unit price, profit margin), so store the numerator and denominator and divide after aggregating.
- **Degenerate dimension** — a business identifier such as order number or invoice number left as a column on the fact table with no dimension of its own, because everything else about it has already been extracted; it enables drill-through and grouping without a pointless one-column table.
- **Junk dimension** — one small table that absorbs several unrelated low-cardinality flags and indicators (order type, payment flag, gift flag) behind a single foreign key, instead of ten near-empty dimensions or ten flag columns on the fact.
- **Conformed dimension** — the same dimension table, or a strict subset of its rows and columns, used identically by every fact table; conformance is what makes drill-across possible, and the bus matrix (bus schema) is the register of which business processes share which conformed dimensions.
- **Role-playing dimension** — one physical dimension joined several times under different aliases or views, e.g. `order_date`, `ship_date` and `delivery_date` all pointing at `dim_date`.
- **Factless fact table** — a fact table with only foreign keys and no measure, used either to record events (student attended a class, an insurance accident) or to record coverage and eligibility (which products were on promotion, so you can find promoted products that did *not* sell); you answer questions by counting rows.
- **Bridge table** — resolves a genuine many-to-many between a fact and a dimension, or between a dimension and a multi-valued attribute (product↔category, account↔customer), optionally carrying an allocation weight so the measures do not double count.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ Star vs snowflake: what is the difference, which is better, and when is snowflake better? — Star keeps each dimension in one flat denormalised table (one hop, simple SQL, fastest, the default); snowflake normalises dimensions into parent tables (`dim_product → product_category → product_manufacturer`), removing redundancy and centralising hierarchy maintenance but adding joins and slowing queries. Choose snowflake for very large or deeply hierarchical dimensions, attributes shared across dimensions, or when the source is already normalised and the load window is tight.
- ★ What is a galaxy schema (fact constellation)? — Multiple fact tables sharing the same conformed dimensions, for example sales and returns facts both joined to `dim_date` and `dim_product`; without conformed dimensions it is just two unrelated stars.
- ★ What is dimensional modelling? — A design technique that stores all data in two kinds of table: fact tables holding the numeric measurements of a business process and dimension tables holding the context those measurements are analysed by.
- ★ What is the difference between a fact table and a dimension table? — Facts record what happened (measurable events, mostly numeric, foreign keys to dimensions); dimensions record who/what/where/when (descriptive, textual, used for filtering and grouping). The relationship is many facts to one dimension row. (devinterview calls it "many-to-many with dimension tables"; that is wrong — fact-to-dimension is many-to-one, which is precisely why star joins are cheap.)
- ★ What is grain, or the level of granularity of a fact table? — The level of detail of one fact row, stated as "one row per order line" or "one row per account per day"; it decides which measures are additive, whether joins fan out, and what can be uniquely identified.
- ★ What are the main types of fact table? — Transaction (one row per event), periodic snapshot (one row per entity per period, such as a daily balance), and accumulating snapshot (one row per process instance, updated in place through the order lifecycle).
- ★ What are semi-additive and non-additive facts? Give examples. — Semi-additive can be summed over some dimensions but not all: a bank account's `current_balance` sums across accounts but not across days. Non-additive cannot be summed over any dimension: `profit_margin` and other ratios must be recomputed from their components after aggregation.
- ★ What is a degenerate dimension? Give an example. — A dimension-like identifier stored on the fact table with no dimension table behind it, because all its descriptive attributes already live in other dimensions; the classic example is the POS transaction number or invoice number. It can serve as part of the fact's primary key but not as a foreign key.
- ★ What is a junk dimension and how does it differ from a degenerate dimension? — A junk (sometimes "dirty") dimension collects unrelated low-cardinality flags and indicators into one small table referenced by a single key; a degenerate dimension is a key kept on the fact with *no* table at all. One creates a table, the other removes one.
- ★ What are conformed dimensions, and what is a conformed fact? — A conformed dimension means the identical thing to every fact table it joins to, so results can be compared and combined across processes; a conformed fact is a measure defined identically across marts so that adding or comparing it is legitimate.
- ★ What is a factless fact table? — A fact table with foreign keys but no numeric measure, used for event tracking (attendance, accidents) and for coverage or eligibility (which products were on promotion) so you can find what did *not* happen; you count rows instead of summing.
- ★ What is a surrogate key and why does a dimension need one? — A meaningless generated integer as the dimension's primary key; it is independent of the source system, immune to business-key changes, cheap to join, and it is the mechanism that lets one business entity have several historical versions (SCD2).
- How do you implement a many-to-many relationship in a star schema? — With a bridge (associative) table between the fact and the dimension, optionally weighted so measures allocate rather than duplicate. (The source answers "use a snowflake schema"; that is wrong — snowflaking normalises a hierarchy, it does not resolve M:N.)
- What is a bridge table and when do you need it? — When one fact row legitimately relates to many dimension members (a product in several categories, an account with several holders); without it the join multiplies rows and every SUM is inflated.
- What is the difference between a dimension and an attribute? — A dimension is the whole analytical axis (product, customer, time); an attribute is one descriptive column inside it (product name, product category).
- Can a dimension table contain numeric values? — Yes, when the number is descriptive rather than measured (year, size, band, postcode); the test is whether you would ever sum it, and if you would, it belongs in the fact.
- Why is the fact table in normal form if denormalisation is what makes a warehouse fast? — The fact table is already almost fully normalised: it contains only measures plus foreign keys, with every descriptive attribute pushed out to dimensions. Denormalisation in a star happens inside the *dimensions*, not the fact.
- What is a critical column? — An attribute whose change invalidates history if you overwrite it: overwrite a customer's city and five years of past purchases appear to have happened in the new city. The fix is a surrogate key plus SCD2.
- How do you load the time or date dimension? — Generate it once with a program that loops over every calendar date in range (often 10–100 years, one row per day), adding weekday, month, quarter, fiscal period and holiday flags; never derive calendar attributes from a timestamp at query time.
- How are dimension tables designed? — Locate the source of the attributes, decide how to extract them, decide the change-tracking policy (SCD type) per attribute, then align the fact table and the load routines with the resulting keys.
- What are the different methods of loading dimension tables? — Conventional load validates all constraints and keys before inserting, so integrity is guaranteed but it is slow; direct/bulk load disables constraints, loads, then validates and quarantines bad rows.
- What is a hierarchy in a dimension, and what is a natural versus navigational hierarchy? — Ordered levels within a dimension that drive drill-down and aggregation (day → month → quarter → year); a natural hierarchy has a genuine parent-child relationship at every level, a navigational one groups levels only for browsing convenience. One dimension can carry several hierarchies.
- What is drilling across? — Combining measures from two different fact tables by querying each at the same conformed dimension attributes and joining the results, rather than joining the two facts directly.
- What are aggregate tables? — Pre-summarised copies of a fact at a coarser grain, kept so common reports do not scan the base fact; they cut query cost but must be refreshed and kept consistent with the detail.
- What are lookup tables? — Reference tables joined on a key to enrich or validate incoming rows during a load; in a dimensional model the dimensions themselves play this role.
- What is a bus schema, or bus matrix? — Kimball's master register of conformed dimensions and standardised fact definitions across business processes; it is the plan that keeps independently built marts joinable.
- What is a core dimension versus a conformed dimension? — A core dimension serves exactly one fact table or mart; a conformed dimension is shared identically across facts and marts.
- Describe the foreign key columns in fact tables and dimension tables. — A fact table's foreign keys are the primary (surrogate) keys of its dimensions; a dimension's foreign keys, when snowflaked, point at its parent/outrigger tables.
- How do you prevent double counting in an analytical model? — Declare and enforce the grain, keep joins many-to-one, never join two facts directly, use a bridge table for real M:N, and define per-metric aggregation rules (SUM vs COUNT DISTINCT vs last value) then reconcile against the source.
- How do you validate a data model after changes? — Row counts and key uniqueness at each layer, totals reconciled against the source system, drill-through checks on known entities, and regression tests on the key business metrics.
- What is a loop in a warehouse schema and how do you avoid it? — When several tables form a closed join path the query engine has more than one route between them, which is ambiguous and slow; break it with an alias/view of one table (a role-playing dimension) or with a context in the BI semantic layer.
- What is the difference between a fact and a measure? — A measure is one numeric column; the fact is the row (the event) that the measures belong to, at the declared grain.
- What is a role-playing dimension? — One physical dimension joined multiple times through aliases or views for different roles, most often `dim_date` reused as order date, ship date and delivery date. (not in sources, but standard)

## Traps
- Answering "snowflake is a normalised star" and stopping — this is the question the reader already fumbled. Name a concrete case (`product → category → manufacturer`), state the cost (extra joins, slower, harder for BI tools and users) and the benefit (no duplicated text, hierarchy maintained in one place), then say which you would pick and why.
- Defining a galaxy schema as "many facts and many dimensions" — the defining property is that the facts *share conformed dimensions*; say the word conformed.
- Confusing degenerate and junk dimensions — degenerate leaves a key on the fact with no table; junk creates one table to absorb several flags. Opposite directions.
- Calling a balance or a stock level additive — it is semi-additive: sum across accounts or products, never across time; use the last value or an average over time.
- Summing a percentage or averaging an average — non-additive measures have to be rebuilt from stored numerator and denominator after the aggregation.
- Designing before declaring the grain — say "one row per ___" out loud first; interviewers use the missing grain statement to find candidates who have only read about star schemas.

## Graph
- **Needs first:** [[relational-modeling]]
- **Leads to:** [[scd-history]], [[warehouse-architecture]]
- **Asked together with:** [[sql-aggregation]], [[bi-visualization]]
