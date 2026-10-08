# Architecture decisions

State whether consumers need per-key ordering, sub-second or minute-level freshness, and historical corrections. Keep a replayable durable log and make serving updates idempotent. A dual-write from processor to lake and serving system can diverge; use a transactional outbox, recoverable sink protocol, or reconciliation strategy and describe the residual failure window.
