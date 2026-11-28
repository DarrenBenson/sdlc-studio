# BG1783: `critic.py approach panel` reports a seat's latest GO without saying it is on an older note, and its roster tells seats to record while their brief forbids it

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_solution_review_panel_brief.py, changelog.d/BG1783.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** US1351's product review in run twenty-eight (2026-11-28), verdict ffd69e96f956-a2fee8c4, by execution; non-blocking, and US1351 has landed.
> **Created:** 2026-11-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M8B7DJ - raised during the run, 2026-11-28T00:42:47Z

## Summary

Two sentences US1351 added mislead a team running a panel. (1) The roster prints each seat's "latest GO at round N" without the GO's digest, so after a note revision every seat can read GO while `approach_agreed` is False (critic.py:7242). By execution on a `[qa, product, persona]` fixture: qa CHANGES at round 1, product and persona GO at round 1 on digest 288a39615844, the note revised, qa GO at round 2 on the new digest, and the roster printed three GOs while the approach was not agreed. `lane land` still refuses, so nothing unagreed lands. (2) The roster says "Each seat writes its reply file and records it with `critic.py approach record`" (critic.py:7250), but every seated brief's Rules say "read-only on the repository, except your reply file" (critic.py:7121), and recording writes sdlc-studio/reviews/solution-reviews.md.

## Steps to Reproduce

1. In a fixture with `review.solution_review.panel: [qa, product, persona]`, record qa CHANGES, then product and persona GO, on a note.
2. Revise the note; record qa GO on the new digest.
3. `critic.py approach panel --unit U` prints a GO for every seat; `approach_agreed` is False.

## Proposed Fix

Print each seat's GO with its digest, or mark a GO on another digest as on an older note; make the roster say the orchestrator records each reply (or let the brief's Rules allow the record), so the two agree. Pin both with tests.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Two sentences US1351 added mislead a team running a panel.
- [ ] **AC2** The proposed fix lands, pinned by a test: Print each seat's GO with its digest, or mark a GO on another digest as on an older note; make the roster say the orchestrator records each reply (or let the...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-28 | sdlc-studio | Filed |
