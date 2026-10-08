# State contract

Persist source identity, last committed sequence, schema version, last output transaction, and update timestamp. State updates must be serialized per source partition or use compare-and-set semantics. Keep secrets outside the checkpoint store.
