"""Dependency-free structural, domain, and uniqueness checks for row mappings."""
from __future__ import annotations

from collections.abc import Hashable, Iterable, Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class Contract:
    required_fields: tuple[str, ...]
    unique_key: str | None = None
    allowed_values: Mapping[str, frozenset[str]] | None = None


@dataclass(frozen=True)
class Violation:
    row_number: int
    rule: str
    field: str


def validate_rows(
    rows: Iterable[Mapping[str, object]], contract: Contract
) -> list[Violation]:
    """Return field-level failures without copying potentially sensitive values."""
    violations: list[Violation] = []
    seen_keys: set[Hashable] = set()
    allowed_values = contract.allowed_values or {}

    for row_number, row in enumerate(rows, start=1):
        for field in contract.required_fields:
            value = row.get(field)
            if value is None or (isinstance(value, str) and not value.strip()):
                violations.append(Violation(row_number, "required", field))

        for field, allowed in allowed_values.items():
            value = row.get(field)
            if value is not None and (
                not isinstance(value, str) or value not in allowed
            ):
                violations.append(Violation(row_number, "allowed_values", field))

        if contract.unique_key is not None:
            field = contract.unique_key
            value = row.get(field)
            if value is None:
                violations.append(Violation(row_number, "unique_key_missing", field))
            elif not isinstance(value, Hashable):
                violations.append(Violation(row_number, "unique_key_unhashable", field))
            elif value in seen_keys:
                violations.append(Violation(row_number, "unique", field))
            else:
                seen_keys.add(value)

    return violations
