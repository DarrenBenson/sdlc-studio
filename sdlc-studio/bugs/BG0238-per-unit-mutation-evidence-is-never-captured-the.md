# BG0238: Per-unit mutation evidence is never captured: the close lane reads the previous sprint's report

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py,.claude/skills/sdlc-studio/scripts/gate.py
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

mutation.py writes a single whole-sprint artefact at sdlc-studio/.local/mutation-report.json stamped with `git_rev`, and `gate._mutation` marks it STALE when `git_rev` != HEAD. That shape assumes exactly one run per sprint, at the close. When mutation is run per unit during the build (the RETRO0061 lesson, applied by hand in RUN-01KY0VNV), each run overwrites the last and every one goes stale as soon as the next unit commits, so by the close NOTHING from this sprint survives. Right now the on-disk report is from run 8c47cc8 with EP0085 targets (critic.py, `run_state.py`, sprint.py) - the PREVIOUS sprint - while RETRO0062 and LATEST.md both state that 8 mutants were killed across BG0231 and BG0232. Those 8 kills exist only as prose. The gate correctly warns STALE and still reports PASS, so the sprint closed with its mutation claim unbacked and nothing said so.

## Steps to Reproduce

1. Run mutation.py scoped to one unit's changed file mid-sprint. 2. Commit that unit, then build and commit the next. 3. python3 scripts/gate.py --only mutation --root . 4. Observe [warn] mutation-report is STALE (run at <old>, tree at <HEAD>) and gate: PASS. 5. Read the report's `target_hashes`: they name the previous run's files, not this sprint's. The per-unit kills are absent from every machine-readable surface.

## Proposed Fix

Make the report accumulative rather than last-write-wins: append each run as an entry keyed by its target set and `git_rev`, and have the gate lane judge COVERAGE of the sprint diff (which changed files have a non-stale mutation entry) instead of freshness of a single blob. A file whose entry predates its own last edit is stale; a file with no entry is uncovered; both are reportable, and the lane can then state what fraction of the sprint's changed surface actually carries evidence. Do not simply re-run at close to refresh the stamp - that discards the per-unit result and pays for the surface twice.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
