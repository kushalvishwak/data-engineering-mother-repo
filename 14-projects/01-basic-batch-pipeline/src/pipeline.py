"""Small, deterministic CSV batch example using only Python's standard library."""
from __future__ import annotations

import csv
import os
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Order:
    order_id: str
    order_date: date
    amount: Decimal


@dataclass(frozen=True)
class Rejection:
    line_number: int
    reason: str


def parse_order(row: dict[str, str], line_number: int) -> tuple[Order | None, Rejection | None]:
    order_id = (row.get("order_id") or "").strip()
    raw_date = (row.get("order_date") or "").strip()
    raw_amount = (row.get("amount") or "").strip()
    if not order_id:
        return None, Rejection(line_number, "missing order_id")
    try:
        order_date = date.fromisoformat(raw_date)
    except ValueError:
        return None, Rejection(line_number, "invalid order_date; expected YYYY-MM-DD")
    try:
        amount = Decimal(raw_amount)
        if not amount.is_finite():
            raise InvalidOperation
    except (InvalidOperation, ValueError):
        return None, Rejection(line_number, "invalid finite decimal amount")
    return Order(order_id, order_date, amount), None


def read_orders(path: Path) -> tuple[list[Order], list[Rejection]]:
    accepted: list[Order] = []
    rejected: list[Rejection] = []
    with path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        expected = {"order_id", "order_date", "amount"}
        if not reader.fieldnames or not expected.issubset(reader.fieldnames):
            raise ValueError(f"input must include columns: {', '.join(sorted(expected))}")
        for line_number, row in enumerate(reader, start=2):
            order, rejection = parse_order(row, line_number)
            if order is not None:
                accepted.append(order)
            elif rejection is not None:
                rejected.append(rejection)
    return accepted, rejected


def aggregate_by_day(orders: Iterable[Order]) -> dict[date, tuple[int, Decimal]]:
    totals: dict[date, tuple[int, Decimal]] = defaultdict(lambda: (0, Decimal("0")))
    for order in orders:
        count, amount = totals[order.order_date]
        totals[order.order_date] = (count + 1, amount + order.amount)
    return dict(sorted(totals.items()))


def _atomic_csv(path: Path, header: list[str], rows: Iterable[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent,
                                         delete=False) as stream:
            temp_name = stream.name
            writer = csv.writer(stream)
            writer.writerow(header)
            writer.writerows(rows)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    finally:
        if temp_name and os.path.exists(temp_name):
            os.unlink(temp_name)


def run(input_path: Path, output_dir: Path) -> tuple[int, int]:
    orders, rejected = read_orders(input_path)
    summary = aggregate_by_day(orders)
    _atomic_csv(output_dir / "daily_summary.csv", ["order_date", "order_count", "amount_total"],
                [[day.isoformat(), str(count), format(amount, "f")]
                 for day, (count, amount) in summary.items()])
    _atomic_csv(output_dir / "rejections.csv", ["line_number", "reason"],
                [[str(item.line_number), item.reason] for item in rejected])
    return len(orders), len(rejected)
