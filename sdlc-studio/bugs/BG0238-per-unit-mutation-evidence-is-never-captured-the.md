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

### Repair after the RUN-01KY2K5R review (REJECT, MAJOR + 2 MINOR)

The review was right and both reproductions stood up as filed.

**What was wrong.** The lane read the ledger and then overlaid the report's own
`target_hashes` on top of it, so any hash-matching file the report NAMED read as evidence.
`mutation.py` computes that field from `files`, outside every verdict and refusal path, so it
names a target no mutant ever reached. Reproduced twice, verbatim: a refused run printed "no
mutants applied, nothing was proven ... mutation evidence covers 1/1 file(s)" in one sentence;
and three changed files with a real green suite and `--max-mutations 1` printed "covers 3/3
file(s)" and PASSED while the ledger correctly held only `a.py`.

**Why the deleted guard was wrong to delete.** Removing `if not report.get("refused")` from
`append_ledger` was justified above with "the verdict rule already excludes every target". That
is true of the LEDGER and was never checked against the consumer reading the report directly,
which is the very thing being written in the same change. The surviving mutant proved the guard
was redundant *in `append_ledger`*; the sentence then generalised it to the report, and the
overlay in `gate.py` made the generalisation false. The guard itself stays deleted - it really
was pinned by nothing - and the rule it expressed is now enforced where it belongs: coverage
cannot see the report at all.

**What the lane does now.**

- `_mutation_coverage(root)` no longer takes the report. Evidence is the ledger alone, so a
  file can be called covered only when the suite returned a killed or survived verdict on it.
- The degraded fallback is REACHABLE, not merely present - the previous MINOR. With no per-file
  evidence, the lane checks the report's own target hashes (the CR0146 behaviour, now carried by
  `_report_hash_stale`), then the whole-blob rev. Verified by execution, not by reasoning: a
  refused run in a fixture repo wrote a report with `target_hashes` and no ledger, an unrelated
  commit moved HEAD, and the lane said `mutation-report is STALE (run at 3076e9920, tree at
  6a73a5251)`; deleting the ledger and editing the target in a non-git fixture gave
  `mutation-report is STALE (target(s) edited since the run: a.py)`.
- `None` and `[]` from `_mutation_changed_surface` no longer collapse - the second MINOR. The
  line names which non-surface it fell back to: "(git could not name the changed files)" against
  "(nothing changed since HEAD)", so a figure about the ledger's own files is never read as a
  figure about this change.
- The survivor summary carries its run. Coverage is per file, the summary is per run, and the
  old whole-blob check said so out loud where the first cut said nothing: the lane now appends
  "summary is from the run at <rev>, not this tree (<head>)". Attribution, not a finding - it
  adds no count, so a covered surface still passes.

**On this repo at HEAD**, where no ledger exists and the report is the previous sprint's:
`3 survived, 0 error(s) of 16 applied (3137 truncated) - advisory - 16/3153 enumerated sampled
(0.5%) - summary is from the run at 8c47cc83e, not this tree (b93ab9c2c); mutation evidence
covers 0/4 file(s) of the changed surface; no evidence: gate.py, run_state.py, mutation.py (+1
more)`. Both things the old lane and the broken lane each got half right.

Seven tests added, one changed. Five were seen RED before the code that makes them pass: the
four reproductions above, and the run-attribution test. Two were GREEN from the moment they
were written and are said so plainly rather than counted as red-first - the negative guard that
an in-tree summary carries NO attribution, and the writer-side test that `target_hashes` names
every target asked for. Both are pinned by mutants instead. The changed one is a signature
(`_boom(root, data)` -> `_boom(root)`), no behaviour.

Eight hand-applied mutants, every one killed, each applied to the file on disk with
`__pycache__` purged and `python3 -B`: restoring the report overlay (kills 3), collapsing the
two fallback labels (1), neutering `_report_hash_stale` (1, and it is the CR0146 test that
catches it), disabling the rev branch (2), making `_key_under` ignore the root (8), dropping the
run attribution (1), making the attribution unconditional (1), and restricting `target_hashes`
to judged targets (1).

`test_gate.py` 224 + `test_mutation.py` 58 green; the whole script suite 3523 green, `tools/`
273 green, style/links/budgets/neutrality/versions clean, `reconcile detect` drift 0.

Not covered here: `help/mutation.md` and the spec docs are still undocumented for the ledger,
unchanged from above. The ledger is also durable across sprints, so the "recorded surface"
figure can span older files - the label says which surface it is, but nothing bounds it to the
current run.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
| 2026-07-21 | claude | Fixed: bounded per-target ledger `mutation-runs.json` beside the unchanged report; gate lane judges content-hash coverage of the git-derived changed surface, degrading to the ledger when git cannot answer; still advisory. 22 mutants applied, 20 killed; the 2 survivors deleted a redundant guard and rewrote a test that pinned nothing. |
| 2026-07-21 | claude | Repaired after review REJECT: coverage read the report's `target_hashes` as evidence, so a refused run and a ceiling-truncated run both reported files no mutant ran on. Evidence is now the ledger alone; the degraded fallback was proved reachable by execution; `None` vs `[]` surfaces are named apart; the survivor summary states which run it came from. 7 tests added and 1 changed: FIVE seen red first (the four reproductions and the run-attribution test), TWO green from the moment they were written and pinned by mutants instead - see the body, which is the honest account. 8 mutants killed. |
| 2026-07-21 | claude | Round-2 review APPROVE, with one MINOR against this unit fixed at close: the `recorded is None` clause in `_report_hash_stale` was a SURVIVING mutant - the guard was copied from the ledger path into the fallback and its test was not, so dropping it left all 224 tests green while a report hash of null read as fresh. Now pinned by `test_a_report_hash_of_null_is_not_evidence_in_the_FALLBACK_either`, and the mutant dies. Third instance this sprint of a guard reading as coverage while pinned by nothing (L-0159). |
