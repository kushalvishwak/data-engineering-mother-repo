# Test plan

Use a fake transport to simulate 200/empty page, 429 with `Retry-After`, transient 503, timeout, token expiry, repeated cursor, malformed JSON, schema drift, and sink failure after raw commit. Assert retries are bounded, cursor advances only after durable archival, and replay does not duplicate curated records.
