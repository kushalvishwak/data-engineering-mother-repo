# State transition model

For interval `I`, read changes after committed offset `c` through candidate offset `n`. Transform deterministically, deduplicate by source key/version, commit output for `I`, then persist `n`. If output commit succeeds but checkpoint write fails, replay `I` must be harmless. If the checkpoint advances first, a crash can lose data; avoid that ordering.
