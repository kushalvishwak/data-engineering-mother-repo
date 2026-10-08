# Example configuration contract

The compact executable accepts input and output paths as function arguments to keep behavior explicit. A production config could add `input_uri`, `output_uri`, `run_date`, `schema_version`, `max_reject_ratio`, and `owner`. Resolve secrets through the platform identity/secret manager, never a checked-in config value.
