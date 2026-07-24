# BG0272: retro accuracy misattributes a run's rung: _run_rung reads the CURRENT run state, so re-running retro/sprint-report for an older retro after a new run opened reads the wrong goal rung

> **Status:** Fixed
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py,.claude/skills/sdlc-studio/scripts/tests/test_nondone_close.py
> **Verification depth:** functional (unit: _run_rung reads the rung recorded on the run being reported, not the current run state; re-run attribution asserted on the value, not the label)
> **Severity:** Medium
> **Points:** 3

## Summary

`retro._run_rung` read `run_state.read(root)["goal"]` unconditionally - the run that is open
NOW, not the run the retro belongs to. Every new run re-stamps that goal, so re-running
`retro accuracy` (or the sprint report, which reads the same batch block) for an older retro
attributes the current run's rung to that older sprint. The reported rung gates the
tokens-per-point rate: a design-rung sprint re-read while a build run is open publishes the
very rate the non-done rung exists to withhold, into the file the planner re-measures from.
The retro is the one artefact whose numbers are supposed to be fixed once recorded.

The elapsed and token reads beside it already refuse a run whose batch does not COVER the
retro's units (`_run_covers`). The rung is a third quantity read off a run and obeyed no such
rule.

## Steps to Reproduce

1. Close a run driven to `--goal design` over a batch, and write its retro; `retro accuracy`
   reports `rung: design` and withholds `sprint_tokens_per_point`.
2. Open a new build run (`goal: done`) over a different batch.
3. Re-run `retro accuracy` for the FIRST retro. Observed: `rung: done`, and a
   tokens-per-point computed over the design sprint's terminal points. Expected: `rung:
   design` and no rate, exactly as at close - the rung belongs to the run that delivered
   those units.

## Proposed Fix

Take the rung from the run record the retro belongs to rather than from whatever run is open:
the live run-state first, then the run archive newest-first, taking the first record whose
batch covers the retro's units - the same coverage rule the elapsed and token reads obey. When
no recorded run covers them the rung is unknown and stays `done`, the documented default, so
the honest build case is never blanked by a lookup that found nothing.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Groomed (symptom, repro, fix) and the AC given an executable verifier in place of `manual`. |
| 2026-07-24 | sdlc-studio | Fixed: `_run_rung(root, unit_ids)` resolves the rung from the covering run record (live state, then archive newest-first); `accuracy` resolves it once and gates the rate on it. Three mutants killed (read the live run unconditionally; walk the archive oldest-first; ignore the matched run's goal). |

## Acceptance Criteria

### AC1: the retro reads the rung of the run it belongs to, not the current run state

- **Given** an older retro is re-run after a newer run has opened (which re-stamps the run-state goal)
- **When** `retro accuracy` reports the batch
- **Then** the rung is the one that run recorded, and the non-done rung still withholds the tokens-per-point rate
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_nondone_close.py::RungBelongsToItsOwnRunTests::test_an_older_retro_reads_its_own_runs_rung_after_a_new_run_opened

### AC2: a run of its own still supplies the rung, and an unattributable retro keeps the build default

- **Given** the retro's own run is still open, or no recorded run covers its units at all
- **When** `retro accuracy` reports the batch
- **Then** the open run supplies the rung, and an unattributable retro reads `done` and keeps its rate rather than being blanked by a lookup that found nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_nondone_close.py::RungBelongsToItsOwnRunTests
