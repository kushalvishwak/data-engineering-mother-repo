# Implementation outline

Keep event parsing and business aggregation independent of the chosen broker. Add a platform adapter for source offsets/checkpointing and a sink adapter with an explicit commit or upsert contract. Pin Spark/runtime version for Structured Streaming code.
