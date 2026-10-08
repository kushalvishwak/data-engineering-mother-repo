# Python interview practice

## How do you process a file larger than memory?

**Short answer:** stream records in bounded batches, and ensure downstream state is bounded too.

**Deep explanation:** a generator only bounds input memory; accumulating results or building a giant deduplication set can still grow without limit. Use external sort/index, partitioned state, or a distributed engine when global operations exceed memory. Set explicit limits and define behavior on malformed rows.

**Example:** iterate a CSV reader and write validated rows to partitioned temporary files, then atomically publish a manifest after all partitions finish.

**Common mistake:** replacing `read()` with a generator while collecting every item in a list later.

**Senior follow-up:** how do you make a multi-file output replay-safe? Use immutable run-scoped objects and publish a commit manifest only after validation; readers consume committed manifests.

## When is concurrency useful in an ingestion client?

**Short answer:** for independent I/O-bound requests, if the source quota and ordering contract permit it.

**Deep explanation:** concurrency improves latency hiding, not source capacity limits. Bound in-flight requests, honor rate limits, propagate cancellation, and make retry policy idempotent. CPU-heavy Python work may need processes or native/vectorized execution; the GIL and serialization costs matter.

**Example:** fetch independent date partitions with a semaphore and per-request timeout, then persist results keyed by partition.

**Common mistake:** unbounded futures and retry storms after a dependency outage.

**Senior follow-up:** how would you avoid overload amplification? Use a concurrency budget, backoff with jitter, circuit breaking where appropriate, and load shedding.
