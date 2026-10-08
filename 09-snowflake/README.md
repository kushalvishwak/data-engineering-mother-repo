# 09 · Snowflake

Understand virtual warehouse compute, storage, micro-partition metadata, pruning, caching, and workload isolation. Keep the distinction between logical SQL design and warehouse sizing clear; benchmark with representative data and concurrency.

Study stages, file formats, Snowpipe, streams/tasks, dynamic tables where applicable, time travel, zero-copy cloning, masking policies, row access policies, and role hierarchy. Streams track change metadata with retention constraints; consumers must account for transactional consumption and staleness.

Exercise: design a role hierarchy and incremental load from staged files, including deduplication, schema drift, warehouse auto-suspend, and cost monitoring. Verify feature behavior against the account's Snowflake edition and current docs.
