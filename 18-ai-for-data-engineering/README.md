# 18 · AI for data engineering

Use AI assistants to accelerate bounded work such as query explanation, test-case brainstorming, documentation drafts, and code review prompts. Engineers remain accountable for correctness, security, licenses, and production behavior.

Do not submit credentials, personal data, regulated data, or proprietary code to a tool without approved controls. Validate generated SQL against dialect semantics and query plans; test generated transformations against adversarial edge cases. Record provenance when generated output materially influences production code.

Exercise: ask an assistant to propose tests for an incremental merge, then independently add cases for duplicate keys, late events, null keys, retries, and deletes. Compare the result to the contract.
