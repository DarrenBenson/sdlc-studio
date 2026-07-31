# BG0464: The coverage gate fails open on a hand-appended supersession: an author retires the REJECT blocking their own work with one line, and the close reports the unit covered by an independent pass

> **Status:** Fixed
> **Verification depth:** functional (the pre-fix truthiness test restored as a mutant and KILLED by the new regression pair; the full skill suite green at 5587)
> **Severity:** Critical
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** Independent adversarial review of RUN-01KYTKA1 tranche E (QA seat, isolated worktree, 41 mutants). US0560=REJECT, US0561=REJECT, US0562=REJECT. Reproduced end to end by the author before repair.
> **Created:** 2026-07-31
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The gate that enforces independent review can be switched off by the party it exists to constrain, with one appended line.

`verdict_for` skipped any row whose `superseded` flag was TRUTHY, of any grade. `_no_negative_verdict` reads it, so a unit carrying a live REJECT lost that REJECT and the verdict-blind evidence lane then reported it covered. `record_supersession` REFUSES to write such a record at write time - it demands a boundary and refuses an authoriser who is the row's own author - but the verdict log is a text file and a hand append walks round the tool. `_is_principal_superseded` exists as exactly that read-time backstop, and its own docstring says so; only `is_independent_signoff` consulted it. The sign-off gate and the coverage gate therefore enforced DIFFERENT independence rules, and the weaker one guarded the honesty check.

The repair: the grade of supersession required scales with the direction the mistake fails. Retiring an APPROVE weakly costs an approval and the gate refuses - it fails closed. Retiring a REJECT weakly removes the only record that blocks the unit, so a REJECT now needs a principal-grade correction.

## Steps to Reproduce

Executed against a fixture, before the repair:

```text
record_verdict(US0001, REJECT, reviewer=independent-qa, author=the-author)
verdict_for -> REJECT

record_supersession(..., authorised_by=the-author, boundary="")
  -> tool REFUSES: needs --boundary naming the separate trust boundary

append by hand to the log:
  SUPERSEDED unit=US0001 row-date=... row-verdict=REJECT
    row-reviewer=independent-qa row-author=the-author
    authorised-by=the-author boundary=- reason=inconvenient recorded=...

verdict_for              -> None      (the live REJECT vanished)
row superseded flag      -> True
_is_principal_superseded -> False     (the backstop knew, and nobody asked it)
```

The reviewer traced the same path through `sprint.py` to `review_coverage -> {covered: True, by: 'adversarial evidence'}`, `uncovered_units -> []` and `_close_review_coverage -> ok=True` printing "1/1 unit(s) covered by an independent pass".

## Proposed Fix

`verdict_for` retires a superseded row unconditionally only when it is not a REJECT. A REJECT is retired only when `_is_principal_superseded` agrees: the correction names a boundary, its authoriser is not the row's own author, and that authoriser did no in-session review work on the unit.

One further weakness noted and NOT repaired here: `-` passes the boundary test, because the check is a non-empty string test and `-` is non-empty. `-` is this repo's own placeholder for absent, and it is accepted as a named trust boundary in three places - `record_supersession`, `_is_principal_superseded` and `is_independent_signoff`. Filed as part of the residue rather than widened into this repair.

## Acceptance Criteria

### AC1: a hand-appended author supersession cannot retire a blocking REJECT

- **Given** a live REJECT and a supersession appended by hand naming the row's own author as authoriser and `-` as boundary
- **When** the verdict is read
- **Then** the REJECT still stands, because `record_supersession` refuses to write such a record and the read-time backstop that exists for the hand append is now consulted by the coverage gate as well as the sign-off gate
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::SupersededGateTests::test_a_HAND_APPENDED_author_supersession_cannot_retire_a_blocking_REJECT
- **Verified:** yes (2026-07-31)

### AC2: a principal-grade supersession still retires a REJECT

- **Given** a correction naming a boundary, authorised by someone who is neither the author nor an in-session reviewer of the unit
- **When** the verdict is read
- **Then** the row is retired as before, so the repair narrows the rule rather than refusing to correct anything
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::SupersededGateTests::test_a_PRINCIPAL_supersession_still_retires_a_reject
- **Verified:** yes (2026-07-31)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-31 | Claude Opus 5 | Filed |
| 2026-07-31 | Claude Opus 5 | Repaired: `verdict_for` retires a superseded row unconditionally only when it is not a REJECT; a REJECT needs `_is_principal_superseded` to agree. AC3 (the two gates sharing one backstop) is met by construction of this repair and is covered by AC1's mutation. |
