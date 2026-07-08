"""Refund validation (SPEC R6)."""
from __future__ import annotations

from decimal import Decimal

from models import Refund


class RefundError(ValueError):
    """Raised when a refund breaches SPEC R6."""


def validate_refund(
    refund: Refund, captured: Decimal, already_refunded: Decimal
) -> None:
    """Reject refunds that take the aggregate beyond the captured amount."""
    if refund.amount <= 0:
        raise RefundError("refund amount must be positive")
    if already_refunded + refund.amount > captured:
        remaining = captured - already_refunded
        raise RefundError(
            f"refund {refund.refund_id!r} of {refund.amount} exceeds the "
            f"remaining captured amount ({remaining}) for order "
            f"{refund.order_id!r}"
        )
