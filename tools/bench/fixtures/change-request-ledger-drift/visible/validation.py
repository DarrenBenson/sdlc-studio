"""Order validation and money arithmetic (SPEC R2, R5)."""
from __future__ import annotations

from decimal import ROUND_HALF_EVEN, Decimal

from models import Order

TWO_PLACES = Decimal("0.01")


class ValidationError(ValueError):
    """Raised when an order fails validation."""


def round_currency(amount: Decimal) -> Decimal:
    """Round to two decimal places using half-even rounding (R5)."""
    return amount.quantize(TWO_PLACES, rounding=ROUND_HALF_EVEN)


def compute_total(order: Order) -> Decimal:
    """Recompute the order total from its line items (R2).

    The ``claimed_total`` on the order is never consulted.
    """
    total = sum(
        (item.unit_price * item.quantity for item in order.line_items),
        Decimal("0"),
    )
    return round_currency(total)


def validate_order(order: Order) -> None:
    """Raise :class:`ValidationError` when the order is malformed."""
    if not order.order_id:
        raise ValidationError("order id must be non-empty")
    if not order.line_items:
        raise ValidationError("order must have at least one line item")
    for item in order.line_items:
        if item.quantity <= 0:
            raise ValidationError(
                f"line item {item.sku!r}: quantity must be positive"
            )
        if item.unit_price < 0:
            raise ValidationError(
                f"line item {item.sku!r}: unit price must not be negative"
            )
