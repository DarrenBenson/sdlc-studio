# CR-0069: harden shared table-parser edge cases plus regression battery (review WS B1a)

> **Status:** Proposed
> **Created:** 2026-06-22
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Feature

## Summary

World-class review WS B1a. The reconcile fault history (multi-schema columns, count blocks, orphan safety) all flow through the one shared `lib/sdlc_md.py` table parser. The parser is hardened but its edge-case test breadth is uneven and consumer call-sites lack a regression battery.

## Acceptance Criteria

- [ ] new `scripts/tests/test_table_parsers.py` exercises the shared parser + every call-site (reconcile/critic/rfc/ledger/conformance/integrity) on: escaped pipes, ragged/short rows, empty cells, whitespace, unicode, multi-schema column positions
- [ ] each reconcile-lineage edge case has a permanent regression test
- [ ] if a live bug surfaces, raise a BG; else the battery is pure hardening

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-22 | sdlc | Created via `new` (deterministic) |
