# Failure matrix

| Failure | Response |
|---|---|
| Timeout, 429, transient 5xx | Bounded retry; honor `Retry-After`; retain cursor |
| Expired credential / 403 | Stop and alert owner; do not retry-loop |
| Cursor repeats or page loop | Stop, record cursor fingerprint, alert |
| Schema mismatch | Archive raw page, quarantine normalization, notify contract owner |
| Sink commit fails | Keep extraction checkpoint; retry idempotent upsert |
| API retention expires before recovery | Escalate source reconciliation; document irrecoverable interval |
