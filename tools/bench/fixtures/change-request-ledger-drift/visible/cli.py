"""Command-line entry point: load orders from JSON and print a summary."""
from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal
from pathlib import Path

from ledger import Ledger
from models import Customer, LineItem, Order


def load_orders(path: Path) -> list[Order]:
    """Parse a JSON array of orders into model objects, verbatim (R8)."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    orders: list[Order] = []
    for item in raw:
        customer = Customer(
            name=item["customer"]["name"],
            email=item["customer"]["email"],
        )
        line_items = tuple(
            LineItem(
                sku=li["sku"],
                quantity=int(li["quantity"]),
                unit_price=Decimal(str(li["unit_price"])),
            )
            for li in item.get("line_items", ())
        )
        claimed = item.get("claimed_total")
        orders.append(
            Order(
                order_id=item["order_id"],
                customer=customer,
                line_items=line_items,
                claimed_total=Decimal(str(claimed)) if claimed is not None else None,
            )
        )
    return orders


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Record a batch of orders into a fresh ledger."
    )
    parser.add_argument(
        "orders_file", type=Path, help="JSON file containing an array of orders"
    )
    args = parser.parse_args(argv)

    ledger = Ledger()
    for order in load_orders(args.orders_file):
        entry = ledger.record_order(order)
        line = f"{entry.status.upper()} {entry.order_id} {entry.total}"
        if entry.reason:
            line += f" ({entry.reason})"
        print(line)
    accepted = sum(1 for e in ledger.entries if e.status == "accepted")
    print(
        f"{accepted} accepted, {len(ledger.entries) - accepted} rejected, "
        f"{len(ledger.customers)} customers"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
