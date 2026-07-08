"""Duplicate-customer detection (SPEC R3, R7, R8).

R3: duplicates are exact matches on the pair (name, email).
R7: name comparison is case-sensitive; names differing only by case
    are distinct customers.
R8: comparison must never mutate the records it inspects.
"""
from __future__ import annotations

from collections.abc import Iterable

from models import Customer


def comparison_key(customer: Customer) -> tuple[str, str]:
    """Key used for duplicate detection: exact (name, email) match (R3)."""
    return (customer.name, customer.email)


def find_duplicate(
    existing: Iterable[Customer], candidate: Customer
) -> Customer | None:
    """Return the stored customer the candidate duplicates, if any."""
    key = comparison_key(candidate)
    for customer in existing:
        if comparison_key(customer) == key:
            return customer
    return None
