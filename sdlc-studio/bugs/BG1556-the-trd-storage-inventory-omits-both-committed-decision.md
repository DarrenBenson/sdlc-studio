# BG1556: The TRD storage inventory omits both committed decision stores and does not tell the two decisions ledgers apart

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** sdlc-studio/trd.md, tools/tests/test_lean_trd_refresh.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, trd lens, survived 3 of 3 refute votes; observed at sdlc-studio/trd.md section 6 Storage Strategy and 'Committed evidence and records' table (lines 526-558); section 5 rule 5 (292-293); against sdlc-studio/decisions/ (33 files), sdlc-studio/decisions.md, scripts/ledger.py:4,29 and scripts/decisions.py:8
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:28:56Z

## Summary

The TRD's ADRs and revision rows cite D-numbered decisions as their authority, and its table of committed evidence and records claims to list what is committed. Neither decision store is in it: `sdlc-studio/decisions.md`, the D-numbered log that `decisions.py` writes, and the per-tranche files under `sdlc-studio/decisions/` that `ledger.py` writes. The only mention is rule 5 of section 5, which says `decisions.py` appends to the decisions ledger, the name the other script's files carry in their own heading, and `ledger.py` is missing from that write-surface list altogether. The test that guards the table scans four named directories only, so both stores are exempt by enumeration. A rebuild from this TRD would have no home for the rulings its own ADRs depend on.

## Steps to Reproduce

1. Search sdlc-studio/trd.md for the strings decisions.md, ledger.py and decisions/: no line matches.
2. Search the same file for the phrase decisions ledger: the only hit is line 293, in rule 5 of section 5, attributed to `decisions.py`.
3. Open .claude/skills/sdlc-studio/scripts/ledger.py at lines 4 and 29: it writes an append-only per-tranche ledger under sdlc-studio/decisions/.
4. Open .claude/skills/sdlc-studio/scripts/decisions.py at line 8: it says its log is distinct from the per-tranche ledger.
5. List sdlc-studio/decisions/ (33 files) and note sdlc-studio/decisions.md beside it; both are tracked.
6. Read lines 538 to 540 of the TRD: the guarding test checks only retros/evidence, reports, reviews/verdicts and personas/memory.

## Proposed Fix

Add two rows to the committed evidence and records table: the decision log at `sdlc-studio/decisions.md` written by `decisions.py`, and the per-tranche ledger at sdlc-studio/decisions/<tranche>.md written by `ledger.py`, each with its purpose. Reword rule 5 of section 5 so each script is named with its own store, and add `ledger.py` to that write-surface list. Extend tools/tests/`test_lean_trd_refresh.py` so the tracked files under sdlc-studio/decisions/ and the decision log are checked against the table like the four directories it already scans.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The TRD's ADRs and revision rows cite D-numbered decisions as their authority, and its table of committed evidence and records claims to list what is committed.
- [ ] **AC2** The proposed fix lands, pinned by a test: Add two rows to the committed evidence and records table: the decision log at `sdlc-studio/decisions.md` written by `decisions.py`, and the per-tranche ledger...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
