# RETRO-0061: RUN-01KY03GS: bound the close review loop and clear the instruments close-debt

> **Date:** 2026-07-20
> **Batch:** US0261, US0262, US0263, US0264, US0265, BG0217, BG0220, BG0221, BG0222, BG0223, BG0224, BG0225, BG0226
> **Goal:** done
> **Delivered:** 13 / 13   **Blocked:** 0

## Delivered

- **US0261** - the close review counts its rounds on the run state; past `review.max_rounds`
  (default 3) another round is refused, naming the count, the ceiling and the override, and an
  override is recorded so the retro can read it.
- **US0262** - a finding in code the previous round's repair touched is classified a repair
  regression, by file AND line, against the latest round only. Unlocatable findings are
  reported unclassified, never folded into the fresh count.
- **US0263** - a repair regression escalates to revert / redesign / accept-and-file. Another
  patch round is deliberately not offered. Accept-and-file mints a real linked artefact and
  reports its id; the autonomous path records and blocks.
- **US0264** - per-round token cost, with the cumulative total shown when the next round is
  offered. An unmeasured round is named and the total marked PARTIAL, never summed as zero.
- **US0265** - the reviewer brief carries the diff and risk surface but not the prior verdict
  prose, severity labels, round number or asserted conclusion. Narrowed CR0358's AC5
  deliberately so the probe re-execution demand survives.
- **BG0217** - `validate`'s placeholder warning uses the severity spelling the counters count.
- **BG0220** - `verify_ac` resolves paths against the project root, on six surfaces, not two.
- **BG0221** - `refine --into` merges epic criteria instead of duplicating the AC heading.
- **BG0222** - the suite lanes run in a git environment of their own.
- **BG0223** - a run stopped mid-flight can still take the bounded exit.
- **BG0224** - an explicit `--tokens 0` clears a recorded actual.
- **BG0225** - the close-owed detector reads a Batch line's parenthesised units.
- **BG0226** - a dashed retro id no longer mints an invisible velocity row.

## Blocked / deferred

- None blocked. The batch completed 13/13.

## What went well

- **The fan-out held.** Six file-disjoint bugs ran as parallel subagents against a serial
  author-owned cluster, and the file partition was correct: no collisions, no lost work.
- **Three agents beat their brief.** BG0220's sweep found the same defect unfixed in
  `repo_map.py` (BG0228). BG0225's real fix was that `close_owed` had hand-rolled a third id
  regex instead of the canonical matcher, which also fixed a latent miss where a five-digit id
  matched nothing. BG0224 noticed its own writer fix was masked by its tolerant reader.
- **The machinery this project built caught its own incidents.** BG0215's mutation recovery
  restored a stranded mutant after a SIGTERM and said so. CR0363's selection reporting named
  its 98-file selection and warned about five out-of-selection references. The pre-commit gate
  refused a multi-id commit with no `Refs:` trailer. The conformance gate refused a commit over
  three Done stories whose ACs had rotted.

## What was hard / what stalled

- **The repository was nearly destroyed.** The agent fixing BG0222 - a bug about `GIT_*`
  environment leakage - pointed `GIT_INDEX_FILE` at the live repo's `.git/index.lock` and the
  suites emptied the index: 1845 files staged as deleted, a fixture's `git commit` still
  running against `main`. Recovered with `git reset`, no data lost. The filed reproduction
  itself is the hazard: it says to point `GIT_INDEX_FILE` at `$PWD/.git`.
- **The author stopped the whole sprint for one unit's decision.** US0263, US0264, US0265 and
  BG0223 were unblocked by the BG0222 question and were not built while it was outstanding.
  CR0369's `decision defer` exists precisely for this and was not used. Roughly an hour lost,
  and the run's elapsed wall-clock is now polluted. CR-0378 filed.
- **The first mutation run cost 40 minutes and produced nothing.** It mutated TEST files -
  vacuous by construction per L-0157 - with a full-suite command at ~150s per mutant, then hit
  its timeout. Correctly scoped to product files with a scoped command, the re-run took ~10
  minutes and found three real gaps. The technique was not the cost; the scoping was.
- **Four vacuous tests were caught by mutation, not by review.** One was the author's (the
  no-run guard in `review_round_count`, unreachable through the public path so the test passed
  either way). Two were subagents'. One mutation pass reported three survivors and was WRONG -
  the `-k` filter matched only one of three new test names, so the others never ran.
- **The close cost more than the build.** Build was ~75 minutes for 13 units; the close has run
  ~90 minutes with no commits, dominated by the wasted mutation run and repeated full
  `verify_ac` sweeps.

## Lessons

- **A bug about environment pollution must never be reproduced next to a live repo.** The
  filed reproduction was followed literally and emptied the index. Reproduce in a throwaway
  clone, and assert the parent's index hash is unchanged afterwards - that assertion is the
  evidence, not the test count.
- **A guard unreachable through the public path cannot be tested through it.** It still reads
  as coverage. Drive the mechanism directly or delete the guard.
- **Scope a mutation run to product code with a scoped test command.** Mutating test files
  produces expected-vacuous survivors, and a full-suite command multiplies every mutant by the
  slowest lane. Same technique, 5x the cost, none of the extra yield.
- **A test-selection filter is part of the test harness and can silently exclude the tests you
  are relying on.** A `-k` pattern that matches one of three new tests reports survivors that
  are artefacts of the filter.
- **An AC's freshness must cover whether its verifier still exists.** US0097 read
  `Verified: yes` for weeks after the test it named was deleted by an unrelated change; the AC
  text never changed, so nothing looked stale.

## Estimate vs actual

**Were the estimates any good?** The plan forecast a token cost per unit; telemetry recorded
what each one actually cost. This section holds the comparison, so the question is asked every
sprint instead of only when someone remembers to ask it.

<!-- accuracy:begin (generated by retro.py accuracy --write) -->

| Unit | Points | Estimate (plan-time) | Actual | Ratio (est/actual) | Tokens/pt | Size | Wall | Model |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| US0261 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0262 | 5 | 125,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0263 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0264 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0265 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0217 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0220 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0221 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0222 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0223 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0224 | 1 | 25,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0225 | 1 | 25,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0226 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 13 unit(s) measured; 13 of 13 forecast at plan time.**

**Sprint tokens/point: 90,385** (1,265,392 tokens over 14 delivered points, harness-tracked). The token count is deterministic (supply it with `accuracy --tokens N`) - not UNMEASURED. A descriptive velocity, never a target.

**Velocity (points/elapsed-hour): UNMEASURED.** No run-state elapsed for this sprint (an interactive sprint's wall-clock would count operator-away gaps as sprint time). Supply a real elapsed with `accuracy --elapsed-hours H` to record it - descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).
Unmeasured: US0261, US0262, US0263, US0264, US0265, BG0217, BG0220, BG0221, BG0222, BG0223, BG0224, BG0225, BG0226. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=25000`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

- **The recorded 90,385 tokens/point is distorted and should not seed the rate.** It divides
  the FULL sprint's 1,265,392 harness-tracked tokens by the 14 points that are terminal, while
  all 31 points of work were actually done - the 5 stories (17 points) are Ready and awaiting
  independent sign-off, not incomplete. Over the work performed the figure is ~41,000
  tokens/point. This is BG0218's defect inverted: that one guarded against a partial token sum
  over full points, and this is a full token sum over partial points. The same guard needs the
  other direction.
- **The velocity tooling declined to publish pts/elapsed-hour by itself**, stating that an
  interactive sprint's wall-clock would count operator-away gaps as sprint time. That is the
  correct refusal for this run, which contains roughly an hour of exactly that. No elapsed
  figure was supplied, so no misleading row was written.
- **The elapsed wall-clock for this run is POLLUTED and must not be read as a velocity
  measurement.** It contains roughly an hour of idle time while the author waited on a decision
  that blocked one unit out of thirteen. Points-per-elapsed-hour computed over it would
  understate throughput while reading as a measurement, which is precisely the class of
  false-but-plausible number BG0218 and US0279 were built to remove. Record the delivered
  points and the token actual; do not publish a pts/elapsed-hour figure for this run.
- Observed shape for planning, stated as description not target: ~75 minutes of build for 13
  units / 31 points across 9 gated commits, against ~90 minutes of close. The close is now the
  larger half, and roughly 23 minutes of the whole run was the pre-commit suite alone
  (9 commits x ~152s) - which is RFC0048 option B, still unbuilt, and the reason D6 was
  resolved this sprint as "set the budget after option B lands".

## Actions raised

**Are there any CRs or Bugs you want to raise in this project to address any of the
issues found?**

| Finding | Disposition |
| --- | --- |
| A sprint parks the whole batch on one unit's decision | filed CR0378 |
| Mutation yield and cost are not logged as a series | filed CR0379 |
| `critic._read_rows` returned the markdown header as data | filed BG0227 (fixed here) |
| `repo_map` carries BG0220's root-relative defect | filed BG0228 |
| `ts-check` reads a missing spec as clean and exits 0 | filed BG0229 |
| A skill test's git call can reach the parent repository | filed BG0230 |
| A Done story stays green after its named test is deleted | filed BG0231 |
| `ac_fingerprint`, the freshness spine, has no test of its own | filed BG0232 |
| `refine`'s heading truncation and epic T-shirt derivation are unpinned | filed BG0233 |
| A repo-wide-invariant AC retroactively un-Dones itself as the repo grows | filed BG0234 |

## Mutation evidence

Scoped to product files, 16 mutants applied, **13 killed, 3 survived**, 0 errors. All three
survivors were verified as real coverage gaps rather than equivalent mutants and filed as
BG0232 and BG0233. The run named its 98-file test selection and warned that five `tools/tests`
files reference `sprint`, `retro` and `validate` from outside it - none of the survivors fall in
that warned set, so they are not manufactured by the narrow command.

**16 of 3153 enumerated mutants were sampled (0.5%). The 3137 beyond the ceiling are
un-checked, not clean.** An earlier full-scope attempt was killed at 40 minutes and produced no
evidence; it is recorded here as producing none.
