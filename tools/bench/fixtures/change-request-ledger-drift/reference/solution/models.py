"""Data models for the order ledger.

SPEC R8: stored records preserve their input verbatim, so ``Customer``
keeps whatever casing and whitespace it was given. SPEC R9: ledger
appends are immutable, hence the frozen dataclasses.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Customer:
    """A customer exactly as supplied by the caller (R8)."""

    name: str
    email: str


@dataclass(frozen=True)
class LineItem:
    sku: str
    quantity: int
    unit_price: Decimal


@dataclass
class Order:
    order_id: str
    customer: Customer
    line_items: tuple[LineItem, ...]
    claimed_total: Decimal | None = None  # never trusted (R2)


@dataclass(frozen=True)
class LedgerEntry:
    """An immutable ledger row (R9)."""

    order_id: str
    customer_name: str
    customer_email: str
    total: Decimal
    status: str  # "accepted" or "rejected"
    reason: str = ""


@dataclass(frozen=True)
class Refund:
    refund_id: str
    order_id: str
    amount: Decimal
