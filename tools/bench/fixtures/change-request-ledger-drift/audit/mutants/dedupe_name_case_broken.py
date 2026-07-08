"""MUTANT (audit-quiz grading only, never enters a workspace): breaks SPEC R7 by making
the NAME comparison case-insensitive. A cited check for R7 must fail against this."""
from __future__ import annotations

from collections.abc import Iterable

from models import Customer


def _comparison_email(email: str) -> str:
    return email.strip().casefold()


def comparison_key(customer: Customer) -> tuple[str, str]:
    # R7 broken: name is casefolded too, so "Ada" and "ada" collide
    return (customer.name.casefold(), _comparison_email(customer.email))


def find_duplicate(
    existing: Iterable[Customer], candidate: Customer
) -> Customer | None:
    key = comparison_key(candidate)
    for customer in existing:
        if comparison_key(customer) == key:
            return customer
    return None
