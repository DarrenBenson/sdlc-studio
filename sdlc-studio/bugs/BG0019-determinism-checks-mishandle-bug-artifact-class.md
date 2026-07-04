# BG-0019: integrity and audit mishandle the bug artifact class

> **Status:** Closed
> **Severity:** High
> **Reporter:** Autosprint (tooling-honesty-sprint triage)
> **Date:** 2026-06-20
> **Epic:** --
> **Story:** --

## Summary

The determinism checks shipped in the determinism sprint treat a `bug` like a
CR/story, which is wrong for two reasons and currently leaves `integrity.py`
**RED on the repo**:

1. **integrity** requires an `Epic`/`Story` link on bugs (per the link matrix) and
   errors when an **active** bug lacks one. BG0018 is an Open, standalone audit bug
   with no epic, so `integrity check` exits 1. Standalone/pre-triage bugs are
   legitimate; their link should be recommended, not required.
2. **audit** (the tranche-audit) flags a bug as `weak-AC` because a bug has no
   `## Acceptance Criteria` section - it uses Steps/Expected/Fix. Readiness for a
   bug must be judged by repro + fix presence, not AC.

## Steps to Reproduce

1. `python3 scripts/integrity.py check --root .` -> `2 error(s)` (BG0018 Open, no
   Epic/Story), exit 1.
2. `python3 scripts/audit.py check --bugs Open --root .` -> BG0018 `NOT READY:
   weak-AC; link-integrity`.

## Expected

- A bug missing an Epic/Story link is **advisory**, never an error (any status).
- A bug's readiness is judged by repro/fix presence, not by an AC section.
- `integrity check` is green on the repo; `audit --bugs Open` does not flag a
  well-formed bug as weak-AC.

## Actual

`integrity` errors on the active link-less bug; `audit` reports `weak-AC` +
`link-integrity` on every bug.

## Proposed Fix

- **integrity.py:** make a bug's missing required link always `advisory` (a
  `LINK_OPTIONAL` type), regardless of status. Update the reference-outputs.md link
  matrix note: bug Epic/Story is recommended, not required.
- **audit.py:** for `type == bug`, check `_bug_underspecified` (no Steps/Reproduce
  and no Proposed Fix) instead of `_weak_ac`; the link-integrity issue clears once
  integrity stops erroring on bugs.

## Acceptance Criteria

- [x] integrity reports a bug's missing Epic/Story link as advisory (not error) for an Open bug; `check --root .` exits 0.
- [x] audit judges a bug by repro/fix presence: a bug with Steps + Proposed Fix is ready; one missing either is `underspecified`, not `weak-AC`.
- [x] Both fixes are unit-tested; the repo's `integrity check` is green.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (tooling-honesty-sprint) | Fixed - integrity `LINK_OPTIONAL` for bugs + audit `_bug_underspecified`; integrity green; critic-approved |
| 2026-06-20 | Autosprint (tooling-honesty-sprint) | Filed - dogfooding the determinism checks on the backlog surfaced bug-class mishandling; integrity is RED |
