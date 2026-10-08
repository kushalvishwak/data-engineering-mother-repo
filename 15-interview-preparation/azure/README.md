# Azure interview practice

## How do you secure a data pipeline on Azure?

**Short answer:** use workload identities, least-privilege data-plane access, private network paths where required, managed secrets, encryption, and audit.

**Deep explanation:** separate deployment identity from runtime identity; grant access at the narrowest useful scope across ADLS Gen2, Key Vault, Event Hubs, and compute. Validate both control-plane and data-plane permissions. Route diagnostics and review access regularly.

**Example:** an ADF or Databricks workload uses managed identity to retrieve scoped storage access without embedding an account key in code.

**Common mistake:** assuming network isolation alone provides authorization or using broad subscription-level grants.

**Senior follow-up:** how do you investigate access failures? Trace identity, token audience, role assignment scope, ACLs, network route, and diagnostic logs in sequence.

## When would you choose Event Hubs over scheduled file ingestion?

**Short answer:** when event-level latency and continuous consumption justify the operational complexity.

**Deep explanation:** compare latency target, ordering/partition needs, retention/replay, throughput, consumer groups, schema governance, and cost of always-on processing. Scheduled files can be simpler and cheaper for hourly/daily freshness.

**Example:** clickstream alerting may require event streaming; nightly finance reconciliation may be better as a batch feed.

**Common mistake:** streaming solely because data arrives continuously, without a consumer latency requirement.

**Senior follow-up:** how do batch and stream results reconcile? Define shared keys/semantics and a correction or reconciliation path.
