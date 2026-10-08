# 01 · Foundations

Build the mental models behind reliable data systems: files and formats, storage/compute separation, batch and streaming, distributed systems, networking, Linux/process basics, Git, and security boundaries.

## Core concepts

- A pipeline is a sequence of contracts and state transitions, not just a sequence of scripts.
- Distributed execution introduces partial failure, retries, out-of-order completion, and data movement.
- Define freshness, completeness, correctness, and availability in measurable terms before selecting tools.
- Separate control plane (configuration, scheduling, metadata) from data plane (reading and transforming records).

## Exercise

For a daily orders feed, define its owner, schema, event time, late-arrival policy, expected volume, freshness target, recovery point, access classification, and consumer contract. Identify which decisions change if the feed becomes a stream.

See `docs/reliability-basics.md` and `examples/pipeline-contract.md`.
