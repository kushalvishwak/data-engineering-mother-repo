# Runbook

1. Confirm the input file and expected header are present.
2. Run the unit tests and pipeline command from the root README.
3. Check accepted/rejected counts and inspect rejection reasons without exposing source data.
4. Validate the output totals against an independent control total before promoting it to a consumer.
5. If the run fails, preserve the input and error context, correct the cause, and rerun; output writes replace the previous local files only after the replacement file is complete.

This local runbook does not cover multi-user concurrency, object-store commits, or production alerting.
