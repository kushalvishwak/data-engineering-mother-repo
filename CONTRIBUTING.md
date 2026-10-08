# Contributing

Contributions should be original, technically careful, reproducible, and useful to engineers who operate data systems. Keep the numbered learning sequence stable and preserve the distinction between portable concepts and vendor-specific behavior.

## Before submitting

1. Search the existing material and project briefs; extend the best-fit section instead of creating duplicate explanations.
2. State assumptions, input/output contracts, failure semantics, security boundaries, and cost drivers where relevant.
3. Prefer deterministic, dependency-light examples. Label required runtimes, credentials, permissions, and possible billing before any cloud operation.
4. Add tests for executable behavior. Use synthetic data and do not commit generated outputs.
5. Cite primary documentation for changing product behavior, with product/runtime context and review date when useful.
6. External repositories are reference material only. Do not copy code, prose, diagrams, or datasets unless the exact source license permits the intended use; preserve notices and record attribution and license details.
7. Never include credentials, personal data, proprietary production identifiers, or unredacted logs.

## Structure and quality

Use the existing numbered top-level sequence. A topic can use `README.md`, `docs/`, `examples/`, `exercises/`, `projects/`, and `tests/` when each folder adds real value; do not create empty scaffolding. Project implementations should explain architecture, flow, decisions, recovery, monitoring, tests, security, and cost. Label examples that need Spark, Databricks, cloud, or warehouse services as platform-dependent and do not imply they were locally verified.

## Local checks

Run the standard-library suites from the repository root:

```powershell
python -m unittest discover -s 14-projects/01-basic-batch-pipeline/tests -v
python -m unittest discover -s 02-python/tests -v
python -m unittest discover -s 04-data-modeling/tests -v
python -m unittest discover -s 12-data-quality/tests -v
```

For project 01's end-to-end sample run:

```powershell
python 14-projects/01-basic-batch-pipeline/src/run_pipeline.py
```

CI runs the dependency-free tests on supported Python versions. Add the smallest relevant test to a new executable example and update the run instructions when commands change.
