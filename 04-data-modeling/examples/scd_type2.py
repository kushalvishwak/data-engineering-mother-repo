"""Pure in-memory reference for ordered, idempotent SCD Type 2 updates."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable


@dataclass(frozen=True)
class Change:
    business_key: str
    effective_at: datetime
    source_sequence: int
    region: str
    plan: str


@dataclass(frozen=True)
class Version:
    business_key: str
    region: str
    plan: str
    valid_from: datetime
    valid_to: datetime | None
    is_current: bool
    source_sequence: int
    last_change_at: datetime


def apply_changes(
    existing: Iterable[Version], changes: Iterable[Change]
) -> list[Version]:
    """Apply an ordered batch using half-open [valid_from, valid_to) intervals.

    Conflicting duplicate source keys and out-of-order updates fail loudly.
    Historical restatement, hard deletes, concurrent writers, and persistence
    transactions are deliberately outside this reference implementation.
    """
    versions = list(existing)
    current_by_key: dict[str, int] = {}
    versions_by_key: dict[str, list[Version]] = {}
    for index, version in enumerate(versions):
        timestamps = (version.valid_from, version.last_change_at)
        if version.valid_to is not None:
            timestamps += (version.valid_to,)
        if any(timestamp.utcoffset() is None for timestamp in timestamps):
            raise ValueError("effective timestamps must be timezone-aware")
        if version.valid_to is not None and version.valid_to <= version.valid_from:
            raise ValueError(f"invalid validity interval for {version.business_key}")
        if version.is_current and version.valid_to is not None:
            raise ValueError(f"current version has an end time for {version.business_key}")
        if not version.is_current and version.valid_to is None:
            raise ValueError(f"historical version has no end time for {version.business_key}")
        versions_by_key.setdefault(version.business_key, []).append(version)
        if version.is_current:
            if version.business_key in current_by_key:
                raise ValueError(f"multiple current versions for {version.business_key}")
            current_by_key[version.business_key] = index

    for business_key, rows in versions_by_key.items():
        ordered_rows = sorted(rows, key=lambda item: item.valid_from)
        for previous, following in zip(ordered_rows, ordered_rows[1:]):
            if previous.valid_to is None or previous.valid_to > following.valid_from:
                raise ValueError(f"overlapping validity intervals for {business_key}")

    unique_changes: dict[tuple[str, int], Change] = {}
    for change in changes:
        if not change.business_key:
            raise ValueError("business_key must not be empty")
        if change.source_sequence < 0:
            raise ValueError("source_sequence must not be negative")
        if change.effective_at.utcoffset() is None:
            raise ValueError("effective_at must be timezone-aware")
        identity = (change.business_key, change.source_sequence)
        prior = unique_changes.get(identity)
        if prior is not None and prior != change:
            raise ValueError(f"conflicting duplicate change for {identity}")
        unique_changes[identity] = change

    ordered = sorted(
        unique_changes.values(),
        key=lambda item: (item.business_key, item.effective_at, item.source_sequence),
    )
    for change in ordered:
        current_index = current_by_key.get(change.business_key)
        if current_index is None:
            versions.append(
                Version(
                    change.business_key,
                    change.region,
                    change.plan,
                    change.effective_at,
                    None,
                    True,
                    change.source_sequence,
                    change.effective_at,
                )
            )
            current_by_key[change.business_key] = len(versions) - 1
            continue

        current = versions[current_index]
        if change.source_sequence == current.source_sequence:
            if (
                change.effective_at == current.last_change_at
                and change.region == current.region
                and change.plan == current.plan
            ):
                continue
            raise ValueError("source sequence was replayed with different values")
        if change.source_sequence < current.source_sequence:
            raise ValueError(f"out-of-order source sequence for {change.business_key}")
        if change.effective_at < current.valid_from:
            raise ValueError(f"out-of-order effective time for {change.business_key}")
        if (change.region, change.plan) == (current.region, current.plan):
            versions[current_index] = Version(
                current.business_key,
                current.region,
                current.plan,
                current.valid_from,
                current.valid_to,
                current.is_current,
                change.source_sequence,
                change.effective_at,
            )
            continue
        if change.effective_at == current.valid_from:
            raise ValueError("changed attributes require a strictly later effective time")

        versions[current_index] = Version(
            current.business_key,
            current.region,
            current.plan,
            current.valid_from,
            change.effective_at,
            False,
            current.source_sequence,
            current.last_change_at,
        )
        versions.append(
            Version(
                change.business_key,
                change.region,
                change.plan,
                change.effective_at,
                None,
                True,
                change.source_sequence,
                change.effective_at,
            )
        )
        current_by_key[change.business_key] = len(versions) - 1

    return versions
