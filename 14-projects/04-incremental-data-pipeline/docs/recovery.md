# Recovery and backfill

Retain source history longer than the maximum detection and recovery interval. Record run ID, lower/upper offsets, code/schema version, and output commit ID. For backfills, isolate target partitions or use versioned staging, validate reconciliation, then promote atomically. Never silently jump an expired offset.
