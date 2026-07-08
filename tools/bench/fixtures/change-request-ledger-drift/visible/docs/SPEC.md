# Order Ledger Specification

Validation rules for the order/ledger module. Rule numbers are stable
identifiers: code comments, tickets, and change requests reference
them directly. When behaviour changes, the corresponding rule text
must change in the same commit.

## Rules

- **R1 - Unique order ids.** Order ids are unique per ledger: an order
  whose id matches an already accepted order is rejected.
- **R2 - Totals recomputed.** Order totals are always recomputed from
  line items (quantity times unit price). Totals supplied on input are
  never trusted and never stored.
- **R3 - Duplicate-customer detection.** A candidate customer is a
  duplicate of a stored customer when the pair (name, email) is an
  exact match.
- **R4 - Rejected orders recorded.** Orders that fail validation are
  still appended to the ledger, with status `rejected` and a reason.
- **R5 - Currency rounding.** All currency amounts round to two
  decimal places using half-even (banker's) rounding.
- **R6 - Refund ceiling.** The refunds recorded against an order may
  never exceed, in aggregate, the captured amount for that order.
- **R7 - Name comparison is case-sensitive.** In duplicate detection,
  names differing only by case are distinct customers.
- **R8 - Verbatim storage.** Stored records preserve their input
  verbatim. Validation and comparison must never mutate stored data.
- **R9 - Immutable appends.** Every ledger append is immutable;
  entries are never edited in place.
