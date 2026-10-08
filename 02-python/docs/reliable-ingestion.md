# Reliable API ingestion: boundary and recovery

`examples/api_client.py` isolates page reading from transport and injects time/sleep dependencies so tests can cover retries deterministically. It sets a request timeout, caps each response body at 16 MiB, caps pagination at 10,000 pages by default, retries only explicit transient HTTP/network failures, bounds retry count and delay, and rejects cursor loops. Tune page and body limits to the source contract rather than removing bounds without review.

## Production boundary not implemented by the example

The page iterator is not an ingestion transaction. A durable caller should:

1. Identify a source snapshot or stable change window; pagination over a mutating API can otherwise skip or duplicate records.
2. Archive each raw page under an immutable run/page identity and verify the write.
3. Persist the next cursor only after that archive is durable; define how to resume after an archive succeeds but a checkpoint write fails.
4. Normalize through a versioned schema and publish by stable key/version with an idempotent commit.
5. Store credentials outside process arguments and logs, scope the token, and redact request/response diagnostics.
6. Emit run ID, cursor age, page/record counts, retry/429 rates, duration, and failure class without recording raw sensitive values.

`Retry-After` is interpreted as seconds when it is numeric; HTTP-date forms are not parsed in this small example. Production clients should match the API's documented rate-limit and retry contract. Do not retry an unsafe write unless its idempotency semantics are explicit.
