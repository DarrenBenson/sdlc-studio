"""Workspace test suite for the order ledger.

Run with ``pytest`` from the workspace root. New behaviour added to
the module should come with tests here, following this file's style.
"""
from __future__ import annotations

import dataclasses
from decimal import Decimal

import pytest

from ledger import Ledger
from models import Customer, LineItem, Order, Refund
from refunds import RefundError
from validation import round_currency


def make_order(
    order_id: str = "ORD-1",
    name: str = "Ada Lovelace",
    email: str = "ada@example.com",
    items: tuple[LineItem, ...] | None = None,
    claimed_total: Decimal | None = None,
) -> Order:
    if items is None:
        items = (LineItem(sku="WIDGET", quantity=2, unit_price=Decimal("4.50")),)
    return Order(
        order_id=order_id,
        customer=Customer(name=name, email=email),
        line_items=tuple(items),
        claimed_total=claimed_total,
    )


class TestOrders:
    def test_accepted_order_recorded_with_recomputed_total(self):
        ledger = Ledger()
        entry = ledger.record_order(make_order(claimed_total=Decimal("999.99")))
        assert entry.status == "accepted"
        # R2: 2 x 4.50 recomputed; the claimed total is ignored.
        assert entry.total == Decimal("9.00")

    def test_duplicate_order_id_rejected_but_recorded(self):
        ledger = Ledger()
        ledger.record_order(make_order())
        entry = ledger.record_order(make_order())
        assert entry.status == "rejected"  # R1
        assert len(ledger.entries) == 2  # R4: still appended

    def test_order_without_line_items_rejected(self):
        ledger = Ledger()
        entry = ledger.record_order(make_order(items=()))
        assert entry.status == "rejected"
        assert entry.reason

    def test_entries_are_immutable(self):
        ledger = Ledger()
        entry = ledger.record_order(make_order())
        with pytest.raises(dataclasses.FrozenInstanceError):
            entry.total = Decimal("0.00")  # R9


class TestRounding:
    def test_half_even_rounds_down_to_even_neighbour(self):
        assert round_currency(Decimal("2.125")) == Decimal("2.12")  # R5

    def test_half_even_rounds_up_to_even_neighbour(self):
        assert round_currency(Decimal("2.135")) == Decimal("2.14")  # R5


class TestCustomers:
    def test_exact_duplicate_resolves_to_stored_record(self):
        ledger = Ledger()
        first = ledger.register_customer(Customer("Ada Lovelace", "ada@example.com"))
        second = ledger.register_customer(Customer("Ada Lovelace", "ada@example.com"))
        assert second is first  # R3
        assert len(ledger.customers) == 1

    def test_different_email_is_a_new_customer(self):
        ledger = Ledger()
        ledger.register_customer(Customer("Ada Lovelace", "ada@example.com"))
        ledger.register_customer(Customer("Ada Lovelace", "ada@work.example"))
        assert len(ledger.customers) == 2


class TestRefunds:
    def test_refund_within_captured_amount_recorded(self):
        ledger = Ledger()
        ledger.record_order(make_order())  # captures 9.00
        ledger.record_refund(Refund("REF-1", "ORD-1", Decimal("5.00")))
        assert len(ledger.refunds) == 1

    def test_aggregate_over_refund_rejected(self):
        ledger = Ledger()
        ledger.record_order(make_order())  # captures 9.00
        ledger.record_refund(Refund("REF-1", "ORD-1", Decimal("5.00")))
        with pytest.raises(RefundError):
            # R6: 5.00 + 5.00 exceeds the captured 9.00.
            ledger.record_refund(Refund("REF-2", "ORD-1", Decimal("5.00")))
