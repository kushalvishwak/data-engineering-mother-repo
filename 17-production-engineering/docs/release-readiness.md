# Data pipeline release-readiness checklist

Use this checklist as a gate tailored to risk; not every workload needs the same mechanism.

## Change and deployment

- Review source-to-target contract changes and reader compatibility.
- Build one immutable artifact and promote it between environments with environment-specific configuration.
- Separate deployment identity from runtime identity; grant only required data and control-plane permissions.
- Validate infrastructure plans and protect state; detect drift and require review for destructive changes.
- Define code rollback separately from data rollback, schema rollback, and replay.

## Correctness and operations

- Test small deterministic fixtures plus nulls, duplicates, late events, corrupt records, and retry/restart paths.
- Publish only after required completeness, reconciliation, and quality gates pass.
- Emit run ID, logical interval, input/version identity, accepted/rejected counts, output version, and duration.
- Define freshness and correctness SLOs with an owner, actionable alert, and runbook.
- Test the stop condition and recovery instructions before an incident; preserve evidence without leaking sensitive rows.
- Review retention, access, lineage, cost budgets, and decommissioning for the deployed data product.

## Release decision

Record the approver, known risks, rollback/replay procedure, monitoring window, and consumer communication. A green deployment check is not proof of correct business data; reconcile an independent control total or source manifest where available.
