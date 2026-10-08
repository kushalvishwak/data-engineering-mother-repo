# Architecture overview

The job is deliberately a single-process reference: CSV reader → row parser/validator → daily aggregation → temporary CSV → atomic filesystem replacement. Rejections retain line number and reason, not full row payload, to keep the example privacy-conscious. The job is deterministic for the same input bytes and code version.

For production scale, replace in-memory aggregation with a distributed engine only after volume measurements justify it. For object storage, publish immutable output objects and a final manifest/pointer; filesystem rename assumptions do not automatically hold in object stores.
