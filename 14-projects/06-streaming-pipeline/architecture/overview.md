# Architecture

Choose a stable event identity for deduplication and a partition key that balances ordering needs with throughput. Watermark policy defines when old event-time state can be finalized; it is a business correctness choice. If downstream corrections are required, publish retractions or an update-capable sink rather than claiming a final immutable result too early.
