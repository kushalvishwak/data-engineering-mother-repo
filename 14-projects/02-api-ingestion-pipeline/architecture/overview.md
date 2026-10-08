# Architecture

Separate extraction from normalization so archived responses can be replayed when mapping logic changes. A durable cursor/manifest is the checkpoint. Commit raw page and manifest before advancing cursor. A curated sink is keyed by source identity plus source version (or a documented event identity), so page replay is safe.
