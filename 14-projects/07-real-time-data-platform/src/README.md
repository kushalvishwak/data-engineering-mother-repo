# Implementation outline

Split producer contract, schema validation, stream processor, durable archive, serving writer, and reconciliation job. Use adapters and local fakes for failure tests. Deployment code must enforce separate identities and network policies for each component.
