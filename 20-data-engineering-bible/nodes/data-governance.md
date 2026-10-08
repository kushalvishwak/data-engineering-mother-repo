---
id: data-governance
title: Data Governance
tier: 3
priority: should-know
sources: [obenner/data-governance.md, obenner/observability.md, obenner/system-design.md, obenner/cost-optimization.md, devinterview, cookbook]
---

# Data Governance

## Say it in one line
Data governance is the set of owners, definitions, policies and controls that make data discoverable, trusted and legally safe to use — security is one part of it, not a synonym for it.

## Must be able to recite
- **Governance vs security** — security stops unauthorised access and protects confidentiality and integrity; governance also answers who owns the dataset, what its columns mean, how long it is kept, and who approved the last change.
- **Owner, steward, custodian** — the owner is accountable for the dataset and its business definition, the steward maintains quality and metadata day to day, the custodian runs the platform (storage, access, backups); clear roles prevent the "nobody owns it" incident.
- **Data catalogue** — a searchable inventory holding description, owner, schema, classification, lineage, freshness SLA and downstream dashboards; it is where "who else uses this column" gets answered before you drop it.
- **Business glossary vs technical metadata** — the glossary fixes the approved meaning of "active customer" or "net revenue", technical metadata describes tables, types, partitions and lineage; you need both, one for agreement and one for implementation.
- **Lineage** — the table- and column-level map of where data came from and what consumes it; it gives blast radius during an incident and provenance for a regulatory report.
- **Classification** — tag every column (public / internal / confidential / restricted, or PII / sensitive PII / PCI) because masking, access policy and retention all key off the tag rather than off a column name.
- **PII in an analytics platform** — classify the fields, keep them out of marts that do not need them, grant to groups under least privilege, mask or tokenise at the serving layer, log access, and re-certify entitlements on a schedule.
- **Masking vs tokenisation vs encryption** — masking shows a redacted value (last four digits) and is one-way for the viewer, tokenisation swaps the value for a vault-reversible token that still joins if it is deterministic, encryption protects bytes at rest (AES with a KMS-managed key) and in transit (TLS) but yields plaintext to anyone holding the key.
- **RBAC vs ABAC** — RBAC grants permissions to roles and assigns users to roles, ABAC evaluates attributes (department, region, clearance, data classification) at query time; RBAC is coarse but auditable, ABAC scales to combinations but needs a policy engine.
- **Row- vs column-level security** — row-level filters which rows a session sees (their branch, their region), column-level hides or masks whole columns by role; both belong on the table or view in the warehouse, once.
- **Retention** — set per dataset and enforced mechanically with partition expiry, object-storage lifecycle rules and snapshot expiration, never with a manual cleanup script.
- **Right to be forgotten** — GDPR Article 17 requires deleting or anonymising a subject across raw, curated, serving and extract layers; the design that makes it cheap is isolating personal data in one keyed vault table, or encrypting per subject so erasure is deleting a key.
- **Audit trail** — log who queried what, when and from where, plus every grant, revoke and schema change, and keep it queryable for the retention period; "we have logs somewhere" fails an audit.
- **SOX-style change control** — segregation of duties (whoever writes the change does not deploy it), peer-reviewed pull request, ticket linked to the release, and no interactive write access to production `(not in sources, but standard)`.
- **GDPR and DPDP essentials** — lawful basis and consent, purpose limitation, data minimisation, subject rights (access, correction, erasure, portability) and 72-hour breach notification; India's DPDP Act 2023 uses Data Principal and Data Fiduciary vocabulary with consent notice and erasure rights, its rules notified in 2025 and phasing in `(not in sources, but standard)`.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ What is data governance and why does it matter? — The processes, policies and responsibilities that keep data discoverable, trusted, secure and correctly used; without it definitions diverge, access becomes risky and compliance breaks as the platform adds teams.
- ★ How do you handle PII in a data platform? — Classify the sensitive columns, minimise what flows downstream, enforce least privilege, mask or tokenise in the serving layer, and audit access.
- ★ How would you implement the GDPR right to be forgotten in a warehouse or lake? — Find every dataset holding the identifier from lineage, then delete rows in a table format that supports row-level deletes and expire the old snapshots, or crypto-shred by dropping that subject's key, then reprocess derived layers and record the action.
- ★ What is the difference between masking and tokenisation? — Masking redacts the value so it can no longer be recovered by the viewer; tokenisation substitutes a token that only a secure mapping can reverse, which keeps stable identifiers for joins without exposing raw PII.
- ★ What is anonymisation, and is a hashed email address anonymous? — Anonymisation removes any path back to the individual; a hash is pseudonymisation, still personal data, because a small value domain can be brute-forced.
- ★ What is GDPR? — The EU regulation on processing personal data: lawful basis, purpose limitation, minimisation, subject rights including erasure, and mandatory breach notification, with penalties tied to global turnover.
- ★ What is data lineage and why do you need it? — The dependency graph between sources, jobs, tables and dashboards; it answers "what breaks if this changes" and "where did this number come from", which is exactly what an auditor asks.
- What is a data catalogue and what should it contain? — A searchable dataset inventory with descriptions, owners, schema, classification, lineage, freshness or SLA, and links to the dashboards that consume it.
- Who owns a dataset — what do owner, steward and custodian each do? — The owner is accountable for the data and its definition, the steward maintains quality and metadata, the custodian operates the platform underneath.
- ★ What is the difference between governance and security? — Security is access control, encryption and confidentiality; governance also covers ownership, meaning, quality, lifecycle and change management.
- What is the difference between RBAC and ABAC? — RBAC assigns permissions to roles that users hold; ABAC evaluates attributes of user, resource and context against a policy at request time.
- What are row-level and column-level security, and how would you give a branch manager only their branch? — Row-level security applies a predicate bound to the session user (a mapping table from user to branch), column-level security hides or masks the fields they must not see; both go on the shared table or view.
- How do you make data access auditable? — Log every query with user, object, timestamp and source, log grants and administrative actions, retain per policy, and keep the log itself queryable and tamper-resistant.
- What are data retention policies and how do you enforce them? — A per-dataset rule for how long data lives, enforced by partition expiry, storage lifecycle rules and snapshot expiration, aligned to legal requirement rather than to disk cost.
- ★ How do you keep data secure through an ETL process? — Encrypt in transit and at rest, restrict the service account to the minimum objects, never land raw PII in a shared staging area unmasked, and audit every hop, especially in cloud environments.
- ★ Why does metadata management matter? — Governance is unenforceable without it: you cannot classify, restrict, retain or trace data you cannot describe, and lineage plus glossary are what make self-service safe.
- How do you govern a platform many teams share? — One named owner per dataset, isolation and quotas so one team cannot hurt another, shared naming and testing standards, and a catalogue so nobody rebuilds the same table.
- How do you stop two teams reporting different numbers for the same metric? — One approved definition in the glossary, implemented once in a certified model, and downstream tools consume that model rather than re-deriving it.
- How do you prevent a PII column from leaking into a downstream mart? — Propagate the classification tag with the column, block unapproved sensitive columns in CI on the model, and enforce a column-level policy so even a `select *` returns the masked form.
- What classification would you apply to a customer table? — Account and transaction identifiers internal, name/address/phone/email PII, identity numbers and card data restricted, with the strictest tag in a row driving the table's controls.
- What is Kerberos? — A ticket-based network authentication protocol using a trusted key distribution centre, the standard single sign-on mechanism in Hadoop clusters.
- What is a firewall? — A control that filters network traffic by rule, used to isolate data platform subnets so only approved sources and ports can reach the cluster or warehouse.
- Who approved the last change to this table, and how would you prove it? — The deploy is tied to a reviewed pull request and a ticket, the release log is retained, and production has no interactive write access `(not in sources, but standard)`.

## Traps
- Reducing governance to security — the interviewer is listening for ownership, definitions, lifecycle and change control, not just "we use IAM".
- Calling a salted hash anonymised — a hashed phone number, PAN or Aadhaar is re-identifiable by brute force over a small domain, so the regulation still treats it as personal data.
- Answering right-to-erasure with `DELETE FROM` — the Parquet file is immutable and the old snapshot still holds the row, so you must rewrite files, expire snapshots or `VACUUM`, and keep time-travel retention shorter than your deletion promise.
- Forgetting the copies — backups, dead-letter queues, Kafka topics, BI extracts, spreadsheets emailed to a business user and lower environments seeded from production all hold the same PII.
- Implementing row-level security in each BI tool — the control vanishes the moment somebody queries the table directly; put the policy on the table or view.
- Proposing ABAC because it sounds advanced — without a policy engine and trustworthy attributes it becomes unauditable, and "the policy computes it" is not an answer an auditor accepts.

## Graph
- **Needs first:** [[data-quality]]
- **Leads to:** —
- **Asked together with:** [[warehouse-architecture]]
