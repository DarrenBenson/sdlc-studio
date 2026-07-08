"""MUTANT (audit-quiz grading only, never enters a workspace): breaks SPEC R6 by only
checking the single refund against the captured amount, ignoring prior refunds. A cited
check for R6 must fail against this."""
from __future__ import annotations

from decimal import Decimal

from models import Refund


class RefundError(ValueError):
    """Raised when a refund breaches SPEC R6."""


def validate_refund(
    refund: Refund, captured: Decimal, already_refunded: Decimal
) -> None:
    if refund.amount <= 0:
        raise RefundError("refund amount must be positive")
    # R6 broken: prior refunds are ignored, so aggregates can exceed captured
    if refund.amount > captured:
        raise RefundError(
            f"refund {refund.refund_id!r} of {refund.amount} exceeds the "
            f"captured amount for order {refund.order_id!r}"
        )
