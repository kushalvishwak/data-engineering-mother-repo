# Test plan

The unit suite covers parsing, invalid input, aggregation, rejected counts, and output publication. Extend with missing headers, empty input, duplicate order IDs (currently accepted as separate records by contract), negative amounts, non-finite decimals, output failure, and repeat-run determinism. Production tests should add source-to-output reconciliation and a safe replay test.
