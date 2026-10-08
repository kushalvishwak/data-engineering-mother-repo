# Decisions and trade-offs

- **CSV + standard library:** easy to run anywhere; not suitable for large or nested datasets.
- **Decimal for amounts:** avoids binary floating-point rounding for decimal inputs; currency and scale validation are intentionally outside this starter contract.
- **Reject bad rows:** preserves valid work while surfacing failures; a strict publication threshold should be added for production.
- **Atomic local replacement:** prevents readers from seeing a partially written file on a single filesystem; it does not provide a transaction across the two output files.
