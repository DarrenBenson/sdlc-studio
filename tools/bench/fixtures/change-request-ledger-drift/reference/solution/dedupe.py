"""Duplicate-customer detection (SPEC R3, R7, R8).

R3 (as amended by the duplicate-detection change request): the email
comparison is case-insensitive and ignores surrounding whitespace.
R7: name comparison remains case-sensitive; names differing only by
    case are distinct customers.
R8: normalisation happens at comparison time only; the records being
    compared are never mutated.
"""
from __future__ import annotations

from collections.abc import Iterable

from models import Customer


def _comparison_email(email: str) -> str:
    """Normalised form of an email, used only for comparison (R3, R8)."""
    return email.strip().casefold()


def comparison_key(customer: Customer) -> tuple[str, str]:
    """Duplicate-detection key: exact name, normalised email (R3, R7)."""
    return (customer.name, _comparison_email(customer.email))


def find_duplicate(
    existing: Iterable[Customer], candidate: Customer
) -> Customer | None:
    """Return the stored customer the candidate duplicates, if any."""
    key = comparison_key(candidate)
    for customer in existing:
        if comparison_key(customer) == key:
            return customer
    return None
