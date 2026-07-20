# Reviews - LATEST (anchor)

> Derived from the sprint-close review of **RUN-01KXZQF0** (instruments and stops,
> 2026-07-20, RETRO-0060). Supersedes the RETRO-0058 picture.

## Where the pipeline is (2026-07-20)

**RUN-01KXZQF0 is built, verified and reviewed**: 9/9 units, 30 points - Phase 1 of the
approved v5.0 plan (make the measurements trustworthy: BG0215, CR0363, CR0350, BG0218) plus
the two operator-reported High CRs on bounded interaction (CR0369, CR0371). The closing
review **REJECTed at round 1** (2 MAJOR, 5 MINOR, 2 NOTE - every finding carried a ran
reproduction) and **APPROVEd at round 2** after one test-first repair round; the same
reviewer instance re-ran its own reproductions verbatim.

## What shipped

- **BG0215** - a SIGKILLed mutation run cannot poison the next run's restore: originals are
  persisted to `mutation-inflight.json` before each mutant lands and recovered before the
  baseline; an unreadable or non-object sidecar refuses with the git remedy named.
- **CR0363 (US0277, US0278)** - the mutation gate names what its survivors were measured
  against: the statically resolved test selection is reported (honest UNRESOLVED when nothing
  parses; `--ignore`/`--deselect` honoured), and a referencing test file outside the selection
  warns as the manufactured-survivor condition. Advisory, never blocking. This close's own
  evidence run printed both live.
- **BG0218** - VELOCITY.md's Points column is the delivered-points series (artefact-read);
  ratio columns keep their forecast gate; a partial token sum is never divided by the full
  points. RETRO0058's row backfilled live (Points 14).
- **CR0350 (US0279)** - an interactive close captures the harness-tracked token total itself
  (`accuracy --tokens-from-harness`; cache reads excluded) and the velocity row records the
  actual. Preservation lives in the row writer: no re-run can replace a recorded number with
  its absence.
- **CR0369 (US0280, US0281)** - `sprint decision defer/list/resolve`: an undecidable unit is
  set aside while the batch continues; accumulated decisions are asked together as structured
  questions (named options, consequences, recommendation marked with its reason); the close
  renders the pending queue at the stop; the autonomous path records and blocks, never
  defaults.
- **CR0371 (US0282, US0283)** - a blocked close has a bounded exit: `close --file-and-close`
  files administrative blockers as CRs linked to the run, names deferrals in retro + anchor,
  closes with outcome `closed-outstanding`; a hard blocker (red gate, refusing Done gate, a
  goal-less run) refuses the exit; re-runs are refused once filed; every close attempt records
  its outstanding count and re-runs report the shrinking/growing trend.

The three touched suites: 48 mutation + 115 retro + 235 sprint, green; full skill and tools
lanes green at every commit. Mutation evidence over the sprint diff: 15/16 killed, the one
survivor a stubbed test body in a test file (vacuous by construction, not a product defect),
diff coverage honestly reported.

## The CODE leg - two rounds

| Round | Findings | Outcome |
| --- | --- | --- |
| 1 | 2 MAJOR + 5 MINOR + 2 NOTE (all with ran repros) | REJECT |
| 2 | 1 MINOR + 2 NOTE (non-blocking, filed as BG0223/BG0224) | APPROVE |

**Both round-1 MAJORs were truths this sprint creates being destroyed by an ordinary
re-run** - the recorded interactive token actual erased to 0 by a plain `accuracy --write`
(the guard lived only inside the capture flag; moved into the row writer itself), and
`--file-and-close` re-runnable against a closed run, duplicating the CR set and both
annotation sections (now refused). The recurring pattern held a fifth round: the sharpest
defects sat in the gap between the code and its own prose claims.

## Next steps

- **Phase 2** - RFC0048 (write back the operator-settled D3/D6 first: all six rows still
  read Open) and EP0085 / CR0358 (bound the review loop), ending at the falsifiable
  points-per-sprint checkpoint - which BG0218 makes measurable and US0279 prices.
- **CR0373** (new, from the operator's cross-model calibration question) - the interactive
  token capture should record the delivering model, so Opus and Fable rows land in their own
  (project, model) cells.
- **BG0223** (round-2 finding) - file-and-close refuses a budget-spent/stopped run with a
  false "already closed" message. **BG0224** - an explicit `--tokens 0` cannot clear a
  recorded actual. **BG0221** (refine --into duplicate AC heading), **BG0222** (suite lanes
  break under `git commit -a` - hook GIT_* env leak). **CR0351** (backtick-mangled fields)
  still unbuilt.
- Dogfooding frictions filed at this close: **CR0374** (nothing surfaces the window a live
  mutation run has a mutant on the shared tree - the session serialised by hand), **BG0225**
  (the close-owed detector misses a parenthesised unit on a retro Batch line), **CR0375**
  (bare `status.py` errors instead of showing the pillars dashboard). Filing them made this
  very anchor stale mid-close - CR0371's treadmill observed live, with the new trend line
  reading "outstanding set 10 -> 8 (shrinking)".
- Standing: **RFC0046** needs D1 closed or an override; **CR0355** is a launch-day action;
  **CR0319** is the release cut itself. Release freeze holds.

## Lessons this run paid for

L-0155 to L-0157 (RETRO-0060): the hook environment is part of the test environment
(`git commit -a` leaks GIT_* into the suites' own git calls); an upsert told not to
overwrite must REUSE the recorded value, never omit it; a surviving mutant in a test file
is vacuity by construction, not a finding.
