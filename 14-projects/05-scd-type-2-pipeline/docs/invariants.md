# Invariants and edge cases

- At most one current version per business key.
- Versions for a key do not overlap.
- Unchanged tracked attributes do not create a new version.
- A repeated source change is idempotent.
- Source sequence defines ordering; ingestion time is not a substitute.
- Delete behavior is explicit: tombstone version, expiration only, or physical removal under policy.

If a late change falls inside an existing interval, recompute neighboring boundaries and validate all intervals for that key.
