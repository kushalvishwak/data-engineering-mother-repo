# Architecture review exercise

**Scenario:** A business needs daily finance reporting from eight SaaS sources, with a four-hour freshness target, seven years of retention, and restricted customer data. Analysts use Power BI; finance occasionally corrects prior periods.

## Deliverable

Write a one-page design and a diagram that identify:

1. Source extraction and change semantics for each source (snapshot, updated-since, or CDC).
2. Immutable landing, quarantine, curated data, and publication boundaries.
3. Logical run identity, replay/backfill behavior, and the atomic point at which a period becomes visible.
4. Ownership, identity flow, secret handling, encryption, and least-privilege reader/writer access.
5. Freshness and correctness SLOs, reconciliation inputs, alert recipient, and a useful runbook.
6. Storage/compute/query cost drivers and one alternative with its trade-offs.

## Review prompts

- Which assumptions would change the design most if false?
- How do you prevent a rerun from double-counting a corrected period?
- How can a consumer distinguish a complete period from an in-progress load?
- What evidence proves source-to-report completeness without logging sensitive rows?
- Which service choices are reversible, and which create lock-in?

**Stretch:** define a migration sequence that allows the legacy report and new output to be reconciled before cutover.
