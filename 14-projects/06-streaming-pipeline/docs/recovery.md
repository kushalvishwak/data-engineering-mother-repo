# Recovery contract

Checkpoint state, source offset retention, and sink transaction semantics jointly define recovery. If a checkpoint is lost, select a replay offset from retained source history, deduplicate by event ID, and reconcile aggregate output. Never attach an incompatible checkpoint to a changed query without a deliberate migration plan.
