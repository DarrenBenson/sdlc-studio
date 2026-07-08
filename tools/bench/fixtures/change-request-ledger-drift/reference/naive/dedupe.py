"""Duplicate-customer detection.

Quick fix for the support-reported false negatives: normalise the
comparison key so case and whitespace differences no longer slip
through duplicate detection.
"""
from __future__ import annotations

from collections.abc import Iterable

from models import Customer


def comparison_key(customer: Customer) -> tuple[str, str]:
    """Key used for duplicate detection.

    Lowercase and strip both fields so lookups stay consistent even
    when older records were stored with mixed case.
    """
    return (customer.name.strip().lower(), customer.email.strip().lower())


def find_duplicate(
    existing: Iterable[Customer], candidate: Customer
) -> Customer | None:
    """Return the stored customer the candidate duplicates, if any."""
    key = comparison_key(candidate)
    for customer in existing:
        if comparison_key(customer) == key:
            return customer
    return None
