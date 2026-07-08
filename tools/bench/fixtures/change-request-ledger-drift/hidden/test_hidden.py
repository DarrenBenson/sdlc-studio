"""Hidden acceptance suite for the duplicate-detection change request.

Tests 1-2 verify the requested behaviour. Tests 3-8 are regressions on
the adjacent spec rules the change must not disturb. Test 9 is the
drift check: the ticket asked for docs/SPEC.md to be updated to match.
"""
from __future__ import annotations

import re
from decimal import Decimal

import pytest


def _customer(mod, name, email):
    return mod.models.Customer(name=name, email=email)


def _order(mod, order_id, name, email, items=None, claimed_total=None):
    if items is None:
        items = (
            mod.models.LineItem(sku="WIDGET", quantity=2, unit_price=Decimal("4.50")),
        )
    return mod.models.Order(
        order_id=order_id,
        customer=_customer(mod, name, email),
        line_items=tuple(items),
        claimed_total=claimed_total,
    )


# -- New behaviour: the change request itself ---------------------------


def test_1_email_case_insensitive_duplicate(mod):
    ledger = mod.ledger.Ledger()
    first = ledger.register_customer(_customer(mod, "Ada Lovelace", "ada@example.com"))
    second = ledger.register_customer(_customer(mod, "Ada Lovelace", "ADA@Example.COM"))
    assert second is first, "emails differing only by case must be duplicates"
    assert len(ledger.customers) == 1


def test_2_email_surrounding_whitespace_duplicate(mod):
    ledger = mod.ledger.Ledger()
    first = ledger.register_customer(_customer(mod, "Ada Lovelace", "ada@example.com"))
    second = ledger.register_customer(
        _customer(mod, "Ada Lovelace", "  ada@example.com ")
    )
    assert second is first, (
        "emails differing only by surrounding whitespace must be duplicates"
    )
    assert len(ledger.customers) == 1


# -- Regressions on adjacent, unchanged spec rules ----------------------


def test_3_r7_name_case_still_distinct(mod):
    ledger = mod.ledger.Ledger()
    ledger.register_customer(_customer(mod, "ada lovelace", "ada@example.com"))
    ledger.register_customer(_customer(mod, "Ada Lovelace", "ada@example.com"))
    assert len(ledger.customers) == 2, (
        "R7: names differing only by case are distinct customers"
    )


def test_4_r8_stored_record_verbatim(mod):
    ledger = mod.ledger.Ledger()
    ledger.register_customer(_customer(mod, "Ada Lovelace", " Ada@Example.COM"))
    candidate = _customer(mod, "Ada Lovelace", "ada@example.com  ")
    ledger.register_customer(candidate)
    assert ledger.customers[0].email == " Ada@Example.COM", (
        "R8: the stored record must keep its original casing and whitespace"
    )
    assert candidate.email == "ada@example.com  ", (
        "R8: duplicate checking must not mutate the candidate record"
    )


def test_5_r2_totals_still_recomputed(mod):
    ledger = mod.ledger.Ledger()
    entry = ledger.record_order(
        _order(
            mod,
            "ORD-1",
            "Ada Lovelace",
            "ada@example.com",
            claimed_total=Decimal("999.99"),
        )
    )
    assert entry.status == "accepted"
    assert entry.total == Decimal("9.00"), (
        "R2: totals come from line items; the tampered input total is ignored"
    )


def test_6_r5_rounding_still_half_even(mod):
    assert mod.validation.round_currency(Decimal("2.125")) == Decimal("2.12")
    assert mod.validation.round_currency(Decimal("2.135")) == Decimal("2.14")


def test_7_r6_over_refund_still_rejected(mod):
    ledger = mod.ledger.Ledger()
    ledger.record_order(
        _order(mod, "ORD-1", "Ada Lovelace", "ada@example.com")
    )  # captures 9.00
    with pytest.raises(mod.refunds.RefundError):
        ledger.record_refund(mod.models.Refund("REF-1", "ORD-1", Decimal("9.01")))


def test_8_r4_rejected_order_still_recorded(mod):
    ledger = mod.ledger.Ledger()
    entry = ledger.record_order(
        _order(mod, "ORD-1", "Ada Lovelace", "ada@example.com", items=())
    )
    assert entry.status == "rejected"
    assert entry in ledger.entries, "R4: rejected orders still land in the ledger"


# -- Drift check: the spec must move with the code ----------------------


def test_9_spec_r3_updated(workspace):
    spec_path = workspace / "docs" / "SPEC.md"
    assert spec_path.is_file(), "workspace is missing docs/SPEC.md"
    text = spec_path.read_text(encoding="utf-8")
    match = re.search(r"\bR3\b(?P<body>.*?)(?:\bR4\b|\Z)", text, re.DOTALL)
    assert match, "could not locate rule R3 in docs/SPEC.md"
    body = match.group("body").lower()
    assert "email" in body, "R3 no longer mentions the email comparison"
    assert re.search(r"case.?insensitive|ignor\w*\s+(letter\s+)?case", body, re.I), (
        "docs/SPEC.md still describes R3 as an exact email match; the ticket "
        "asked for the spec to be updated to the case-insensitive rule"
    )
