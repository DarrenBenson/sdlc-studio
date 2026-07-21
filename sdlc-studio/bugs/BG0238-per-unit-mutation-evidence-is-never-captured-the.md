# BG0238: Per-unit mutation evidence is never captured: the close lane reads the previous sprint's report

> **Status:** Fixed
> **Verification depth:** functional - the filed symptom was reproduced from the on-disk state (report at 8c47cc8 with the previous sprint's targets, tree at 16b69eb, lane `[warn] ... STALE ... gate: PASS`) and then as a failing test over a two-unit fixture repo. Both halves are mutation-proven by hand: 22 mutants applied, 20 killed on first application, 2 SURVIVED and each drove a change (one redundant branch deleted, one test rewritten to reach the clause it claimed to pin).
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

## Resolution

Fixed as filed, with the staleness key made explicit: evidence is judged per file on CONTENT
HASH, never on a whole-blob rev. A per-file entry stays valid across later commits that touch
OTHER files, which is precisely what lets evidence gathered per unit during a build still be
readable at the close.

1. **Accumulate.** `mutation.py` still writes `mutation-report.json` as the latest run,
   unchanged, so every existing reader (`gate`, `sprint._mutation_note`) and their tests keep
   working. Each run now ALSO appends per-target entries to
   `sdlc-studio/.local/mutation-runs.json`: target path (repo-relative), content hash at run
   time, `git_rev`, `generated_at`, `test_cmd`, and that target's own kill/survive counts. One
   rule decides what is entered - the test command returned a killed or survived verdict on
   that target - so an unviable-only, errored-only or beyond-the-ceiling target is absent, and
   so is every target of a refused run. Bounded at `LEDGER_LIMIT` (200) entries, superseded
   per target, oldest dropped first, with a cumulative `dropped` count and a printed note on
   any run that drops, because silent truncation reads as "we kept everything".
2. **Coverage, not freshness.** `gate._mutation` now reports what fraction of the surface
   carries evidence, naming the gaps: hash matches -> covered; hash differs, or none was
   recorded -> STALE; no entry -> uncovered. The whole-blob `git_rev` check is kept only as
   the degraded fallback for a project with no per-file evidence at all, so the older
   behaviour is subsumed rather than dropped.
3. **The surface** comes from git - staged, unstaged and untracked mutatable non-test files -
   so the lane needs no open sprint run and no sdlc-studio state and works in a consuming
   project. It degrades to the ledger's own recorded files when git cannot answer (no repo, no
   commit to diff, or a root below the repository top) or the tree is clean, which is the
   close-time case. The probe never raises into the gate.
4. **Still advisory** (`blocking: False`) throughout: survivors and gaps are reported, a close
   is never refused.

Against this repo the lane now says what was previously invisible:
`0/8 file(s) of the changed surface; STALE (edited since mutated): run_state.py, retro.py,
verify_ac.py; no evidence: gate.py, mutation.py, repo_map.py (+2 more)` - and still PASSes.

Two hand-applied mutants SURVIVED and each changed the code or the test:

- Removing the `if not report.get("refused")` guard in `append_ledger` killed nothing: a
  refused run has no records, so the verdict rule already excludes every target. The guard was
  a second rule pinned by nothing, and was deleted rather than left reading as coverage.
- The first version of `test_an_entry_with_no_recorded_hash_is_not_evidence` used a file that
  existed, so it never reached the `recorded is not None` clause it claimed to pin. Rewritten
  around an absent target, where the two unknowns really do compare equal.

Not covered here: `help/mutation.md`, `reference-scripts-verify.md`, `trd.md` and `tsd.md`
still describe only `mutation-report.json`, so the new ledger is undocumented for consumers.

Modules: `test_gate.py` + `test_mutation.py`, 275 tests, green, 19s.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
| 2026-07-21 | claude | Fixed: bounded per-target ledger `mutation-runs.json` beside the unchanged report; gate lane judges content-hash coverage of the git-derived changed surface, degrading to the ledger when git cannot answer; still advisory. 22 mutants applied, 20 killed; the 2 survivors deleted a redundant guard and rewrote a test that pinned nothing. |
