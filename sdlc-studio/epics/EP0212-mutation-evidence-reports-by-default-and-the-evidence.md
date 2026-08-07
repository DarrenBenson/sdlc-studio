# EP0212: Mutation evidence reports by default, and the evidence a measured run produces is the evidence the gate reads

> **Status:** Done
> **Derived Point Total:** 16
> **Parent:** CR0537
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0537. Delivers the work CR0537 requested.

## Story Breakdown

- [x] [US0660: A surviving mutant becomes a severity-rated bug and the transition proceeds, and the run names the mode that held it](../stories/US0660-a-surviving-mutant-becomes-a-severity-rated-bug.md)
- [x] [US0661: A measured mutation run records what it applied, attributed to a unit, so the gate is satisfiable by measurement rather than only by self-report](../stories/US0661-a-measured-mutation-run-records-what-it-applied.md)

## Acceptance Criteria (Epic Level)

- [x] `review.mutation_evidence` takes `report` (the DEFAULT), `block`, or `off`, and the resolved value is printed by the close so nobody has to guess which mode a run was held to
- [x] In `report` mode a surviving mutant is FILED as a bug through the shipped filer - naming the unit, the criterion, the mutant and the test that failed to kill it - and the close PROCEEDS; nothing about the run is held
- [x] A filed survivor carries a derived severity rather than a uniform one, so triage has something to sort on: a survivor on a refusal or gate path outranks one on a reporting path, which outranks one on prose
- [x] `block` remains available and behaves exactly as today, so a project that wants the hard bar keeps it by setting one value
- [x] The retro counts survivors filed, by severity, so the trade being made is visible over time rather than felt
- [x] Re-filing is idempotent: the same surviving mutant on the same unit does not mint a second bug on the next run
- [x] One thing still blocks in every mode: a mutant RECORDED as killed that is shown to survive. That is not a quality bar, it is the ledger lying about itself, and this run produced exactly one

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Test Plan

An epic's criteria are the conjunction of its stories', so its rows name the mutant that
answers each - every one applied by hand, run under `python3 -B` with `__pycache__` purged, and
the source restored byte-identically. The epic owns no code of its own, and inventing a mutant
for it would be a row nothing could apply.

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | change sprint.py to default an unrecognised evidence mode instead of refusing it by name (US0660 AC5) | the three modes, and the close names the one that held |
| AC1 | remove the `off` early return, so the lane runs rather than standing down (BG0541 AC6, killed by `test_off_stands_the_lane_down_rather_than_running_and_discarding`) | the three modes, and the close names the one that held |
| AC2 | change transition.py to report the survivor in the warning and mint nothing (US0660 AC1) | a survivor is FILED and the close proceeds |
| AC3 | change transition.py to map severity from the target file's suffix rather than the enclosing structure (US0660 AC3) | a filed survivor carries a derived severity |
| AC4 | delete the `mutation_evidence_lane` call from `_pre_write_gates` - the state of the tree before this work (BG0541 AC1) | `block` remains available and behaves as before |
| AC4 | change transition.py to append the lane's block whatever the lane returned, so every repair refuses (BG0541 AC6) | `block` remains available and behaves as before |
| AC5 | change sprint_report.py to count from a tally the filer wrote rather than from the filed artefacts (US0660 AC6) | the close counts survivors by severity |
| AC6 | change transition.py to key idempotence on a `.local` cache rather than the artefact field (US0660 AC4) | re-filing is idempotent |
| AC7 | change transition.py to gate the contradiction check behind the mode being other than `off` (US0661 AC4) | one thing blocks in every mode |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-07 | sdlc-studio | Closed. Its criteria are the conjunction of its stories', and the Test Plan names the mutant that answers each - the epic owns no code of its own, so a mutant invented for it would be a row nothing could apply |
| 2026-08-07 | sdlc-studio | Plan review REJECTed AC4's row: the mutant it cited changes only the report arm, so `block` stayed selectable and refused exactly as before - a row that cannot fail on the criterion it is attached to. It now cites the two BG0541 mutants that do act on `block` itself. AC1 gains the `off` row the reviewer found missing: US0660 AC5's fixtures are block, absent and a typo, and `off` was covered nowhere in this table |
| 2026-08-07 | sdlc-studio | Plan review round 2 APPROVEd, ruling AC4 CLOSED by execution. Its minor is folded in: the `off` row's rationale said the lane would WARN, and removing the guards makes it REFUSE a false exemption instead - the test it actually kills is the stand-down one, which the row now names |
