---
id: scd-history
title: Slowly Changing Dimensions and History
tier: 0
priority: must-know
sources: [obenner/dwha, obenner/data-modeling, obenner/dbt, devinterview, cookbook]
---

# Slowly Changing Dimensions and History

## Say it in one line
A slowly changing dimension is a dimension whose descriptive attributes change occasionally, and the SCD type is the policy you chose for what happens to the old value when they do.

## Must be able to recite
- **Type 0 — retain original** — the attribute is written once at first load and never updated again (date of birth, account open date, original credit score); any later source change is ignored on purpose.
- **Type 1 — overwrite** — update the column in place and keep no history; correct for fixing genuine data errors, wrong the moment anyone asks what the value was last quarter, because all past facts silently inherit the new value.
- **Type 2 — add a new row** — close the current version and insert a new one, so the dimension holds one row per version of the business key; this is the default answer whenever the requirement is history or as-of reporting.
- **Type 3 — add a new column** — keep `current_address` next to `previous_address`; gives exactly one step of history and no more, so use it only when the business genuinely wants a before/after comparison.
- **Type 4 — history table / mini-dimension** — keep the base dimension current-only and push either the full history or just the fast-changing attributes into a separate table, which stops a volatile attribute from exploding the main dimension.
- **Type 5 — Type 4 plus Type 1** — the base dimension carries a Type-1 outrigger key to the *current* mini-dimension row, so you can report both "profile at the time" and "profile as of now".
- **Type 6 — hybrid (1 + 2 + 3)** — Type 2 rows for history plus a `current_*` column on every row that is overwritten Type-1 style, so one dimension answers both as-of-then and as-of-now; the sources' "hybrid SCD" (some columns Type 1, some Type 2) is the same family.
- **Type 2 columns** — a surrogate key (the row's own primary key), the natural/business key, `effective_from`, `effective_to`, `is_current`, and usually a `version` number, a change hash and a load timestamp.
- **Type 2 load algorithm** — for each incoming row, look up the current version by business key; if the tracked attributes differ, set the old row's `effective_to` to the new row's start and `is_current = false`, then insert the new row with a fresh surrogate key, `is_current = true` and an open `effective_to`.
- **Hash diff** — store one MD5/SHA hash of the concatenated tracked attributes and compare that single column instead of thirty columns; it makes change detection cheap and makes the list of tracked columns explicit rather than buried in a WHERE clause.
- **Half-open intervals** — use `effective_from <= t < effective_to`; overlapping or gapped intervals are the classic SCD2 bug and they either duplicate or drop facts on an as-of join.
- **Current row convention** — either `effective_to IS NULL` or a high sentinel such as `9999-12-31`; the sentinel is more common because range predicates and BETWEEN then work without special NULL handling.
- **As-of join** — to reproduce a historical report you join the fact's event date into the dimension on the business key with `event_date >= effective_from AND event_date < effective_to`, *not* on `is_current = true`.
- **The fact stores the version, not the entity** — because the fact's foreign key is the surrogate key of the row that was current at event time, old facts keep pointing at old attribute values automatically; the price is that counting rows in the dimension no longer counts customers, so filter `is_current` or use `COUNT(DISTINCT business_key)`.
- **Rapidly changing dimension, slowly changing fact, late-arriving member** — an attribute that changes constantly gets a mini-dimension or banded values (age band, not age); a measure restated after the fact is corrected either by a reversing row plus a new row (audit-friendly) or by rewriting the partition; a fact whose dimension member does not exist yet gets an inferred placeholder row (unknown key) that is filled in later.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ What is a slowly changing dimension, and what are the types? — A dimension whose descriptive attributes change rarely (a customer moves, a product is repriced, a state is renamed). Type 0 never updates, Type 1 overwrites, Type 2 versions with new rows, Type 3 adds a previous-value column, Type 4 splits history into another table, Type 6 combines 1, 2 and 3.
- ★ How do you implement SCD Type 2 — which columns, and what happens on a change? — Columns: surrogate key, business key, `effective_from`, `effective_to`, `is_current` (plus version and hash). On a detected change, set the current row's `effective_to` to the new row's start and `is_current = false`, then insert the new version with a new surrogate key and an open end date; you must also define how changes are detected and how late-arriving updates are handled.
- ★ What is a Type 2 version dimension? — The same thing under a different name: a dimension that keeps both the current record and the full history by versioning rows rather than overwriting them.
- ★ What is a hybrid SCD (Type 6)? — Type 2 rows for the attributes the business tracks, combined with Type-1 overwrite behaviour for the ones it does not care about, and often a `current_*` column on every historical row so the same table supports as-of-then and as-of-now reporting.
- ★ What is SCD Type 1 and when is it right? — Overwrite in place with no history; correct for genuine corrections (a misspelt name, a bad postcode) and for attributes nobody reports on historically, wrong whenever "as at" reporting is required.
- ★ What is SCD Type 3 and what does it buy you? — An extra column holding the previous value alongside the current one; it gives one generation of history with no row growth and no join complexity, and nothing beyond that, so it suits "compare old and new territory" style questions only.
- ★ Why does a Type 2 dimension need a surrogate key, and what is a critical column? — A critical column is one where overwriting rewrites the past: change a customer's city to Hyderabad and five years of Bangalore purchases appear to have happened in Hyderabad. Because the fact stores the surrogate key of the version current at event time, each historical fact keeps its original context. The business key alone cannot do this, since it is no longer unique once you have versions.
- Which SCD type would you use for a customer changing address in a bank, and why? — Type 2, because regulatory and trend reporting has to show the address that was on file when each transaction happened; Type 1 would retrospectively move historical activity to the new branch or region.
- After we build an SCD table, can we still use that dimension as a dimension in a star schema? — Yes. An SCD2 dimension is an ordinary dimension; the fact simply joins on the surrogate key, and current-state reports add `is_current = true`.
- What are the common challenges with SCDs? — Load performance as the dimension grows, correctness under concurrent or out-of-order updates, and query complexity: after Type 2 a row count is no longer an entity count, so every consumer has to filter `is_current` or aggregate on the business key.
- What are the different methods of loading dimension tables? — Conventional load validates constraints and keys before insert, so integrity is guaranteed but it is slow; direct/bulk load disables constraints, loads fast, then validates and excludes bad rows from the index.
- What are snapshots in dbt and when would you use them? — dbt's built-in SCD2: it captures the history of a mutable source table into `dbt_valid_from`/`dbt_valid_to` rows. The `timestamp` strategy trusts an `updated_at` column, the `check` strategy compares a named column list instead — use snapshots whenever you need point-in-time analysis of a source that overwrites in place.
- How do you reproduce a report exactly as it looked last quarter? — Join the fact's event date into the dimension version interval (`event_date >= effective_from AND event_date < effective_to`) rather than filtering on `is_current`; that is the whole reason Type 2 exists.
- Which columns do you actually track in a Type 2, and how do you decide? — Only the attributes the business reports on historically; every extra tracked column produces more versions. Write the list down, hash exactly those columns, and treat everything else as Type 1.
- Should `effective_to` equal the next version's `effective_from`, or one day earlier? — Either works, but you must pick one and use it everywhere: set `effective_to = next effective_from` and use a half-open predicate (`>= from AND < to`), or subtract one unit and use BETWEEN. Mixing the two conventions is what produces duplicate or missing facts.
- How do you handle a change that should have been applied last month (late-arriving dimension update)? — Insert the version in the middle of the timeline: split the affected interval, fix the neighbouring `effective_from`/`effective_to` values, and re-point any facts loaded in that window at the correct surrogate key.
- How do you handle a fact that arrives before its dimension member exists? — Insert an inferred/placeholder dimension row keyed on the business key (or route the fact to a reserved "unknown" key), then update the placeholder in place when the real attributes arrive.
- What is SCD Type 0? — Retain the original value: the attribute is loaded once and never changed, which is the right policy for immutable facts about an entity such as date of birth or original signup channel. (not in sources, but standard)
- What are SCD Types 4 and 5, and what problem do they solve? — Type 4 moves history, or just the volatile attributes, into a separate history table or mini-dimension so the main dimension stays small; Type 5 adds a Type-1 pointer from the base dimension to the *current* mini-dimension row so you can also report by today's profile. Both exist to stop a rapidly changing attribute from multiplying the dimension. (not in sources, but standard)
- What is the difference between SCD and CDC? — CDC is how you detect and deliver changes out of the source system (log reading, triggers, watermark queries); SCD is how you decide to store them in the target dimension. CDC gives you the change, SCD says whether to overwrite it, version it or ignore it. (not in sources, but standard)

## Traps
- Saying "Type 2 adds a new row" and nothing else — name the columns (`surrogate key, business key, effective_from, effective_to, is_current`) and describe the close-then-insert step; that specific detail is what the question is testing.
- Filtering on `is_current = true` in a historical report — that returns today's attributes for yesterday's facts, which is exactly the bug Type 2 was built to prevent; use the effective-date range join.
- Forgetting that the fact table joins to a *version*, not to a customer — after Type 2 the dimension's business key is no longer unique, so any `COUNT(*)` or naive join on the business key inflates results.
- Claiming Type 3 gives history — it gives one previous value; the third change overwrites the second, so it is not a substitute for Type 2.
- Comparing every column to detect change — use one hash of the deliberately chosen tracked columns, otherwise a meaningless change in an untracked field (a whitespace fix, a re-derived flag) creates a spurious version.
- Applying Type 2 to a fast-changing attribute — that produces millions of versions; band the value or split it into a mini-dimension (Type 4) instead.

## Graph
- **Needs first:** [[dimensional-modeling]]
- **Leads to:** [[cdc-ingestion]]
- **Asked together with:** [[dbt-transformations]]
