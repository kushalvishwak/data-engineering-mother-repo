# Implementation outline

Define interfaces for `read_changes(offset)`, deterministic `transform`, idempotent `write_changes`, and `commit_offset`. Use a fake source/sink to test crash points before integrating a database or CDC platform.
