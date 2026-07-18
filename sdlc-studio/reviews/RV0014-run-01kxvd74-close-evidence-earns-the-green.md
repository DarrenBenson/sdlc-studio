# RV-0014: RUN-01KXVD74 close: evidence earns the green

> **Date:** 2026-07-19
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1

## Scope

The closing review of sprint RUN-01KXVD74 (EP0075 verify-line integrity + the seven open bugs),
covering `ba6908e~1..HEAD` - 10 delivered units, 35 files, ~1,163 insertions before repairs. One
CODE leg: an independent adversarial full-diff pass, run as a separate instance from the author,
with every finding required to carry a reproduction the reviewer had actually executed.

Document legs: `CHANGELOG.md`, `sdlc-studio/trd.md` (the 9 threat-model row), and the ten
groomed units. Each is consistent with the shipped code and enforced by the gate.

## Findings

Three rounds: **REJECT, REJECT, APPROVE.**

### Round 1 - REJECT (2 MAJOR, 3 MINOR)

- **MAJOR** `ac_scope.py` - a story-frequency suppression added by this sprint counted the OWNER
  epic's own stories. An epic's backlog is exactly where its title vocabulary appears, so three
  sibling stories dropped the keyword from `distinctive` entirely and deleted a genuine
  multi-keyword cross-epic leak before its strength was computed - the case the new
  `_BLOCKING_STRENGTH` existed to preserve. It also demoted nothing already demoted: 11 findings
  before, the same 11 after. The author's test filed its stories under a non-owning epic, so it
  never reached the branch.
- **MAJOR** `verify_ac.py` - `[no tests to run]` and `[no test files]` were unanchored substrings
  and are normal per-package output of a PASSING `go test ./...`. A green multi-package suite was
  judged vacuous and its author told to re-point a Verify line at tests that demonstrably ran.
- **MINOR** `tools/tests/test_trd_freshness.py` - the new guard grepped the whole TRD for writer
  filenames that appear throughout it, and passed with rule 5 rewritten back to a single writer:
  the exact state BG0187 exists to catch.
- **MINOR** `handoff.py` - `refresh` re-stamps run identity from ambient run state even when the
  batch is scoped. Not reachable via the shipped close path. Filed **BG0198**.
- **MINOR** `retro.py` / `next_id.py` - two id readers disagree on meta-id width. Not reproduced
  against a real project. Filed **BG0199**.

### Round 2 - REJECT (2 MAJOR, both created by the round 1 repair)

- **MAJOR** the counter-signature added to fix the go false positive was **blob-wide**, so any
  co-running tool printing "N passed" disarmed the vacuity gate outright. A false alarm was
  traded for a silent failure, in the sprint whose stated goal is that a green must mean a test
  ran. The reviewer also showed the go signature was dead either way, because the test binary
  prints `PASS` on the same stream as the warning.
- **MAJOR** the replacement comment claimed the retained `_SHARED_EPIC_THRESHOLD` "discounts the
  owner". It does not. One owner story plus one unrelated epic erased both keywords of a real
  leak - worse than the reviewer's own example. The false claim was the stated reason to accept
  the repair.

### Round 3 - APPROVE

Both round-2 reproductions re-run and fixed. Vacuity is now decided per runner family from that
family's own output; `unittest` and `pytest` print one exclusive summary each and need no veto,
and only `go` (per package) and `jest` (per project) can report "nothing here" beside a real
result. The owning epic no longer counts towards a keyword's spread. CR0113 suppression intact
(13 findings, 0 blocking - no flood). Nine honest-green shapes produce no false positive. Five
mutants applied with bytecode purged, all killed. Suites 2,974 + 222 green, drift 0.

The reviewer withdrew one of its own round-2 reproductions as malformed.

## Accepted residuals

- `go` and `jest` keep a narrow per-family veto that line-anchored foreign output could still
  switch off. Inherent to per-unit runners, and far narrower than the blob-wide defect it
  replaced.
- No go or jest toolchain on this machine, so those output formats rest on documented behaviour
  rather than measurement. Recorded as a limit of the evidence, not a defect.
- 13 further duplicated Verify selectors remain across the workspace beyond the four US0227
  owned. Now reported by the new lint on every run rather than silent.

## Verdict

**APPROVE.** Two blocking rounds, both repaired and re-verified by the same reviewer against its
own reproductions. Recorded as a sprint-level verdict over all 10 units in
`reviews/sprint-review-record.md`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-19 | sdlc-studio | Closing review of RUN-01KXVD74 recorded: REJECT, REJECT, APPROVE |
