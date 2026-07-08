"""Append-only order ledger (SPEC R1, R4, R9)."""
from __future__ import annotations

from decimal import Decimal

from dedupe import find_duplicate
from models import Customer, LedgerEntry, Order, Refund
from refunds import validate_refund
from validation import ValidationError, compute_total, validate_order


class Ledger:
    """Holds the customers, order entries, and refunds for one ledger."""

    def __init__(self) -> None:
        self._customers: list[Customer] = []
        self._entries: list[LedgerEntry] = []
        self._refunds: list[Refund] = []

    @property
    def customers(self) -> tuple[Customer, ...]:
        return tuple(self._customers)

    @property
    def entries(self) -> tuple[LedgerEntry, ...]:
        return tuple(self._entries)

    @property
    def refunds(self) -> tuple[Refund, ...]:
        return tuple(self._refunds)

    def register_customer(self, customer: Customer) -> Customer:
        """Return the canonical stored record for this customer.

        A duplicate (per SPEC R3/R7) resolves to the already stored
        record; otherwise the customer is stored verbatim (R8).
        """
        existing = find_duplicate(self._customers, customer)
        if existing is not None:
            return existing
        self._customers.append(customer)
        return customer

    def record_order(self, order: Order) -> LedgerEntry:
        """Validate and append an order.

        Orders that fail validation are still appended, with status
        ``rejected`` and a reason (R4). Entries are immutable and are
        never edited in place (R9).
        """
        total = Decimal("0.00")
        status, reason = "accepted", ""
        try:
            validate_order(order)
            if any(
                entry.order_id == order.order_id and entry.status == "accepted"
                for entry in self._entries
            ):
                raise ValidationError(
                    f"order id {order.order_id!r} already recorded (R1)"
                )
            total = compute_total(order)
        except ValidationError as exc:
            status, reason = "rejected", str(exc)
        customer = self.register_customer(order.customer)
        entry = LedgerEntry(
            order_id=order.order_id,
            customer_name=customer.name,
            customer_email=customer.email,
            total=total,
            status=status,
            reason=reason,
        )
        self._entries.append(entry)
        return entry

    def captured_amount(self, order_id: str) -> Decimal:
        """Total captured for an order (zero when unknown or rejected)."""
        return sum(
            (
                entry.total
                for entry in self._entries
                if entry.order_id == order_id and entry.status == "accepted"
            ),
            Decimal("0.00"),
        )

    def refunded_amount(self, order_id: str) -> Decimal:
        """Aggregate refunds already recorded against an order."""
        return sum(
            (r.amount for r in self._refunds if r.order_id == order_id),
            Decimal("0.00"),
        )

    def record_refund(self, refund: Refund) -> Refund:
        """Append a refund after checking it against SPEC R6."""
        validate_refund(
            refund,
            self.captured_amount(refund.order_id),
            self.refunded_amount(refund.order_id),
        )
        self._refunds.append(refund)
        return refund
