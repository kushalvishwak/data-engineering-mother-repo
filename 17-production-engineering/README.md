# 17 · Production engineering

Production readiness includes tested changes, deployment controls, observability, incident response, security, capacity planning, and retirement. Define SLOs for freshness and correctness; attach alerts to actionable runbooks.

Build CI/CD around repeatable artifacts, environment promotion, identity separation, schema compatibility checks, and rollback/recovery. Infrastructure concepts include declarative desired state, reviewed plans, state protection, drift detection, and least privilege. Separate code rollback from data rollback.

Exercise: write a runbook for a pipeline that succeeds operationally but publishes half the expected rows. Include evidence to collect, safe stop conditions, replay procedure, communication, and prevention follow-up.
