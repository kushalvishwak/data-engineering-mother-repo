# Databricks interview practice

## How do Delta Lake schema evolution and enforcement differ?

**Short answer:** enforcement rejects incompatible writes by default; evolution is an explicit policy for accepting compatible schema changes.

**Deep explanation:** schema evolution can make additive source changes easier but can also silently broaden a contract. Review column/type changes, nested structures, reader compatibility, downstream consumers, and table protocol/runtime requirements. Apply scoped options rather than enabling broad evolution without governance.

**Example:** approve an additive nullable field after checking consumers and table contract; quarantine a type change that alters meaning.

**Common mistake:** treating automatic schema evolution as validation or accepting every source change.

**Senior follow-up:** how do you roll out a breaking change? Version the interface, migrate consumers, backfill if required, and retire the old contract after measured adoption.

## What does Change Data Feed enable?

**Short answer:** it exposes row-level changes between table versions for downstream incremental processing.

**Deep explanation:** consumers must understand change types, version boundaries, retention, enablement time, and replay requirements. CDF does not remove the need for idempotent sinks or schema compatibility. Verify availability and behavior in the selected runtime.

**Example:** propagate changed customer rows to a search index using a versioned checkpoint and idempotent key.

**Common mistake:** assuming CDF is an indefinite event archive.

**Senior follow-up:** what if a consumer falls behind retention? Rebootstrap from a consistent snapshot and resume from its corresponding version, with reconciliation.
