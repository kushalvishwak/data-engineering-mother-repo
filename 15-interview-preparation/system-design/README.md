# System design interview practice

## Design a batch platform for hourly reporting and daily reprocessing.

**Short answer:** use replayable source intervals, idempotent transformations, atomic publication, governed storage, and observable quality gates.

**Deep explanation:** clarify source change semantics, volume, freshness, late data, consumers, security, RPO/RTO, and retention. Separate ingestion checkpoint from output publication; maintain backfill isolation and data contracts. Choose orchestration/compute after identifying workload boundaries.

**Example:** land immutable files with manifests, validate to a quarantine path, transform by source interval, publish partition versions, then advance a durable commit marker.

**Common mistake:** drawing services before clarifying data guarantees or stating “exactly once” without end-to-end sink semantics.

**Senior follow-up:** how do you scale to many domains? Federate product ownership with shared platform contracts for identity, catalog, deployment, observability, and cost attribution.

## Design a streaming architecture for late events.

**Short answer:** define event time and lateness policy, retain replayable offsets, checkpoint state, and support corrections downstream.

**Deep explanation:** choose partition/order key, watermark, state retention, output mode, sink semantics, and source retention. Explain behavior beyond the watermark and recovery if state/checkpoint is lost. Monitor event age rather than only processing throughput.

**Example:** finalize 10-minute windows after a bounded lateness interval and publish compensating updates for accepted late corrections.

**Common mistake:** treating a watermark as a guarantee that no later events exist.

**Senior follow-up:** how do you prove correctness? Compare against a batch recomputation over retained events and measure reconciliation deltas.
