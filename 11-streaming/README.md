# 11 · Streaming

Reason about event time, processing time, watermarks, late data, state, offsets, checkpoints, and delivery semantics. “Exactly once” is end-to-end only when the source, processing state, and sink transaction behavior jointly support it.

Structured Streaming uses incremental execution and checkpointed progress. A checkpoint is tied to query identity and compatible source/sink configuration; do not casually reuse it for a different query. Select output mode and watermark from the business correction policy, not convenience.

Exercise: aggregate click events into 10-minute event-time windows with a 20-minute lateness policy. Specify duplicate handling, state growth, restart behavior, and how a corrected late event reaches downstream users.
