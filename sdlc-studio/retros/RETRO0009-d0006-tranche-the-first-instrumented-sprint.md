# RETRO-0009: D0006 tranche - the first instrumented sprint

> **Date:** 2026-07-04
> **Batch:** BG0052, CR0150, BG0051 (operator-reviewed and ordered, D0006; run on operator redirect, D0008)
> **Goal:** done
> **Delivered:** 3 / 3   **Blocked:** 0

## Delivered

- **BG0052** - terminal transitions record telemetry: the loop's real close path feeds
  `telemetry.jsonl` with no second call; events record on ENTERING the terminal set only.
  This bug's own close wrote the repo's first records.
- **CR0150** - status/hint print the concurrent-session workspace advisory (ids named, no
  authorship guessed, silent without git). Filed by the session that hit the collision.
- **BG0051** - verify_ac write-backs apply bottom-up; root cause REFINED during delivery
  (compounding index shift across top-down insertions, not the filed anchor hypothesis);
  US0051-54 repaired by strip-and-regenerate, 0 misplaced.

## Critic loop, observed

First pass: request-changes - one HIGH (the pillars text-mode wiring dead behind a
misplaced return, shipped green because only the helper was tested), one medium (a bug
lifecycle recorded 3-4 telemetry events), two lows. All four fixed test-first; the critic
re-ran its own repros and approved. Lesson L-0004 recorded: test the command, not only
the helper. Residual cosmetic limitations (git-quoted paths, untracked-dir collapse)
accepted and documented.

The mutation gate then earned its keep on its own sprint: 2 SURVIVORS on the changed
surface - both in the wholly-unpinned `_print_update_notice` - killed by writing the
pinning test the survivors demanded (10/12 -> 11/12; the last survivor is a mutation of
a TEST file's cleanup guard, raising the should-tests-be-surface policy question, logged
to CR0152's reporting territory).

## First instrumented close

`telemetry show --summary` now reads real sprint data (this tranche's closes, plus a few
pre-dedupe duplicates from BG0051/BG0052's own transitions - gitignored local data, read
accordingly). From here, re-scope rates, critic loop shapes, and close-path coverage are
rows, not anecdotes.

## Actions

- [ ] Backlog: CR0151 (seat-score provenance) and CR0152 (sampling-coverage disclosure +
      the tests-as-surface policy note) remain Proposed - the only open items.
- [ ] Watch: telemetry duplicates pre-dedupe in the local file; test-file mutation policy.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | claude | Sprint close retro (created via `artifact new --type retro`) |
