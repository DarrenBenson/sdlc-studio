# BG0536: a test fixture that accepts a caller-supplied root can write into the working tree, and one did - destroying 23 recorded mutation registrations

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_transition.py, tools/lint-style.sh, tools/tests/test_check_spec_claims.py
> **Evidence:** RUN-01KZCAJX, 2026-08-07, during US0565's delivery. `git status` showed an untracked `src/`; `sdlc-studio/.local/mutation-runs.json` had been reduced to a single entry carrying no units, against 23 registrations across BG0530, BG0533, BG0524, BG0521 and BG0516 made an hour earlier. `sdlc-studio/bugs/BG0001-x.md` and `src/thing.py` had reached a commit via `git add -A`. All 23 registrations were re-recorded and re-verified with `mutation.py run --story <id> --from-plan`.
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

A fixture helper in `SurvivorGateTests` takes the directory to build under as a parameter. A placeholder call left in the class passed `"."`, so every run of that test wrote `src/thing.py`, a fake `sdlc-studio/bugs/BG0001-x.md` and - worst - `sdlc-studio/.local/mutation-runs.json` into the REAL repository.

The mutation ledger is not merely a cache. It is the record the terminal-transition gate reads, and overwriting it destroyed 23 mutation registrations covering five delivered units. Because `.local/` is gitignored, git could not restore them; they had to be re-recorded by hand. The fake bug file and `src/` were also swept into a commit by a `git add -A`, so the damage reached history as well as the tree.

The defect is not the placeholder. It is that a fixture CAN address the working tree at all: a helper whose root is a parameter will eventually be called with the wrong one, and the failure is silent because writing to a real path looks exactly like writing to a temp path until you check what changed.

## Steps to Reproduce

1. Any fixture helper of the shape `def _repo(self, d, ...)` that builds under `Path(d)`. 2. Call it with `"."` - a placeholder, a copy-paste, or a refactor that loses the temp-dir context. 3. The test passes. 4. `git status` shows untracked files in the repo root, and any gitignored state the fixture writes is destroyed with no way to recover it from version control.

## Proposed Fix

Make the fixture refuse rather than trusting its callers: assert the resolved root is under `tempfile.gettempdir()` and raise otherwise. Applied to `SurvivorGateTests._repo` already; the same shape exists in other fixture helpers across the suite and should be swept.

Better still as a lane: a guard asserting that no test writes outside a temp directory. The suite runs 6197 tests and a single one writing into the tree is invisible in the pass count - which is how this ran repeatedly before `git status` happened to be checked for an unrelated reason.

And `.local/` deserves a second look. A record the gate reads, that git cannot restore, is one incident away from unrecoverable at any moment - not only from a test.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: A fixture helper in `SurvivorGateTests` takes the directory to build under as a parameter.
- [ ] **AC2** The proposed fix lands, pinned by a test: Make the fixture refuse rather than trusting its callers: assert the resolved root is under `tempfile.gettempdir()` and raise otherwise.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Filed |
