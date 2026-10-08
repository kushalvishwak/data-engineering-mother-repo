# Implementation outline

Suggested modules: `client` (timeouts/auth/retry), `extract` (pagination and raw archive), `normalize` (versioned mapping), `sink` (idempotent upsert), and `run` (checkpoint orchestration). Inject transport and clock to make retry behavior deterministic in tests.
