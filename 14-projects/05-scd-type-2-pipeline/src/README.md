# Implementation outline

Implement a pure transition function from prior versions plus ordered changes to new versions. Keep persistence in a separate adapter. Add a database-specific transactional merge only after the temporal invariants pass against an in-memory reference model.
