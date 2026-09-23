# Back to basics: a whole-project review

> **Date:** 2026-09-23
> **Asked by:** the operator, after RUN-01M33WJ3 was sealed
> **Method:** read-only. Three evidence passes, then six area reviews run in parallel.
> Six headline figures were re-derived by a second read. Every number below names its source.
> **Plan:** `~/.claude/plans/unified-splashing-moler.md` (approved)

## The verdict

The process now spends most of its effort on itself.

- **Where the work goes.** 82% of the last 116 sprint units built or repaired the sprint,
  review and gate machinery, or tooling used only in this repo. The last three runs delivered
  nothing a consuming project would notice.
- **What the machinery produces.** It no longer delivers the three things the operator needs
  to know:
  1. **Estimate accuracy.** It cannot be told.
     - Planned points are overwritten by resized points.
     - No time forecast exists.
     - The token forecast uses a constant the code has refused to re-fit since the history
       began to span two models.
  2. **Delivered to plan.** It is reported, but rework is erased. The last report says "1
     round" for a run of fifteen rounds.
  3. **Known issues.** They are reported, but buried in 14 sections and a 22-row checklist.

This is not a lack of rigour. It is a ratchet:

- every failure became a lesson, every lesson became a gate, and no gate was ever removed;
- every gate generates refusals, the refusals generate bugs in the machinery, and those bugs
  become the next sprint.

The fix is to cut the ratchet, not add another turn to it.

## What the operator asked for, and where the evidence stands

| Complaint | Evidence | Verdict |
| --- | --- | --- |
| Goals are too long and not about value | 12 recent goals: median ~218 words, maximum 500; none names a user outcome. RUN-01M306PY managed 24 (`.local/run-archive/*.json` `sprint_goal`) | **Confirmed** |
| It stops without reason | 24 designed operator touchpoints; ~23 stop points inside one `close`; close attempts per run rose from 1 to 13; RUN-01M33WJ3's close took 12.8 h (`sprint.py:9481-9703`, run archive) | **Confirmed** |
| It asks questions personas could answer | 23 of 31 sampled operator decisions were persona-answerable (D0180-D0229). No code path lets a persona resolve a deferred question: `decision resolve` is operator-only (`sprint.py:11626`) | **Confirmed** |
| Reviews go round after round | The 2-3 round cap (D0146, D0175) is enforced nowhere: `critic.review_round_guard` has no production caller. One run recorded 18 rounds. The documented fix-then-re-review path cannot clear a REJECT (fingerprint mismatch, `critic.py:709-748`), so every REJECT also needs a repair-ledger row (367 rows, 1.3 MB) | **Confirmed, with a structural cause** |
| The report is too complicated | 14 sections, 22 checklist rows (`templates/core/sprint-report.md`, `sprint_report.py:960-1048`) | **Confirmed** |
| Lessons do not deliver full value | 8 of 9 recurring failure classes kept recurring after their lesson was recorded (LL0053: ~17 more hits). About 2% of ~487 lessons ever reach a brief, and every brief for eight weeks has carried the same 5 titles | **Confirmed** |

Where the evidence cuts the other way:

- **Delivery review rounds 1 and 2 do find real defects.** In RUN-01M33WJ3, 9 of 10 REJECT
  rounds changed production behaviour.
- **Plan-review REJECTs are the waste.** 60% of plan reviews rejected (255 of 428), and their
  566 recorded fixes changed test plans, not code.

The lean process keeps one delivery review and deletes plan review.

## The evidence

### Where the time goes

| Measure | Figure | Source |
| --- | --- | --- |
| Commit hook, full suite (median of 10) | 1,309 s | `.local/gate-timings.json` |
| Commit hook, selected suites | 540 s median (214-1,095) | same |
| Push gate | 678 s median | same (`boundary-push`) |
| CI on a green push | ~78 min: the suite runs twice (1,665 s, then 2,347 s under coverage) | CI run 35197242831 |
| CI on main | 43 of 76 pushes red, 34 of them in 3-13 Aug (ripgrep missing on the runner) | `.local/ci-runs.json`, job logs |
| Run span | 14.5-59.6 h per run | run archive |
| Close attempts across 61 archived runs | 206; blocking stages: gate 107, sign-off 65, installed-copy 39, done-gate 34 | run archive |

### What one bug must produce before it is Fixed

The requirements:

1. a test plan;
2. a plan review;
3. Verify stamps;
4. registered mutants, all killed;
5. line coverage of added lines;
6. a verification-depth tier;
7. a four-ledger review trail (verdict, evidence, repair, sign-off);
8. a changelog fragment and index row.

After that, the push runs revert-check and module-alone. 1,052 of 1,062 registered mutants
were killed, so it is a costly signal that is almost never red.

### Size

| Area | Now (lines) | Lean estimate | Source |
| --- | --- | --- | --- |
| `sprint.py` + `lib/run_state.py` | 14,503 | ~1,800 | area 1 review |
| Review and evidence (`critic`, `verify_ac`, `mutation`, `transition`, `conformance`, `readiness`, `persona_resolve`) | 20,369 | ~1,800 core + ~1,100 opt-in | area 2 review |
| Reporting and records (`sprint_report`, `retro`, `reconcile`, `file_finding`, `artifact`, `sdlc_md`, ...) | ~25,900 | ~2,500 | area 3 review |
| `gate.py`, hooks, `tools/` (with their tests) | ~42,000 | ~14,000 | area 4 review |
| Docs: reference, help, templates, SKILL/AGENTS/README | ~48,300 | ~27,800 | area 5 review |
| `lessons.py` | 2,045 | ~800 | area 6 review |

- Production code overall is 86k lines, and roughly two-thirds of it can go.
- The product surface outside the sprint loop is mostly kept: PRD, TRD, TSD, personas, epics,
  stories, audit, repo map, migrate.
- Tests (135k lines) shrink with the code they pin. Most of the 20,441-line `test_sprint.py`
  pins deleted surface, including dead functions.

## Why it got this way: six root causes

1. **Rules became gates, and gates were never retired.** LL0027 ("gate the rule in the command
   people run") was applied to every lesson, with no matching rule for removal.
   - The result: 18 pre-commit lanes, 20 gate lanes, 20 transition gates and 223 refusal
     messages.
   - Two advisory lanes have produced 19,958 findings and no recorded fix.
2. **Review cannot converge by construction.**
   - No round cap is enforced.
   - A fixed unit cannot be cleared by its re-review.
   - Plan review argues over wording.
   - Two verdict writers apply different rules.
3. **Only the operator can decide.** There is no persona `rule` verb and no store of
   precedent, so the same class of question comes back to the operator run after run.
4. **The machine works on itself.** Refusals produce findings about the machinery, the
   findings fill the next batch, and the goals describe the machinery.
5. **Learning records but does not feed back.**
   - Calibration refuses to fit across models, so every plan uses the 25k seed while
     actuals run at about 276k per point.
   - Lessons are printed, not injected. Repeats are minted as new lessons instead of counted.
   - The project lessons log is gitignored, which breaks its own lesson LL0029.
6. **Slow feedback.**
   - A 9 to 22-minute commit (selected or full suite), an 11-minute push and a 78-minute CI
     make every step expensive.
   - An expensive step invites batching, and batching invites the next gate.

## The process, as is and to be

| Step | As is | Cost today | To be |
| --- | --- | --- | --- |
| Goal | A multi-clause paragraph plus a blocking seat review over rounds (45-70 cumulative rounds) | Hours of rounds before code | **One sentence of user value, 20 words or fewer.** One advisory seat read |
| Plan | About 12 gates in `cmd_plan` (462 lines), then an operator triage STOP | Several refusals per run | Select, order, and estimate points + time + tokens from fitted rates. **Operator approves once.** Approval defines the operating domain, pushes included |
| Per-unit spec | Plan review (60% REJECT) plus a separate test-plan review | 3.65 rows per bug | **Deleted.** Criteria quality is part of the one review |
| Build | TDD, Verify stamps, mutant registration, line coverage, depth tier | 8 evidence obligations | TDD to criteria; Verify selectors green. Mutation and coverage opt-in |
| Review | Uncapped rounds, 4 ledgers, per-unit sign-off panel | 1,104 verdict + 776 sign-off + 367 repair + 453 evidence rows | **One reviewer, at most 2 rounds, enforced in code.** Round 2 re-checks the fixes only. A round-2 REJECT is carried as a known issue and the run continues |
| Questions | Operator only | ~74% avoidable interruptions | **Persona `rule` verb**, binding, precedent-checked, logged |
| Commit | 18 lanes plus suites | 540-1,309 s | Lint staged files plus affected tests, **90 s budget** |
| Push | Suite, module-alone, rehearsal, revert-check | 678 s | **Full suite once**, ~3-4 min |
| CI | Suite twice, conformance, corpus | ~78 min | **Suite once** under coverage, ~10 min |
| Close | 9 early stops, 10-step chain, 3 report holds, 22-row checklist | 1 to 13 attempts, up to 12.8 h | **One command:** one-page report, 3-line retro, handover, calibration re-fit |
| Sign | `sign` accepts any named report and never re-checks the tree | - | One command that checks the tree and the report it seals |
| Learn | 487 prose lessons, 5 frozen titles in briefs, seed rate forever | No measured effect | Rates re-fitted at close; ruling precedent; lessons keyed by failure class that graduate into checks; recurrence shown |

The operator is reached only when the andon cord is pulled: an irreversible action outside the
approved plan, or an exit from the operating domain (RFC0060 D4, kept).

## The one-page report

The front page answers three questions:

1. **How accurate were the estimates?**
   - One row each for points, time and tokens: forecast, actual, ratio.
   - Per-unit detail sits beneath.
2. **Did we deliver to plan?**
   - Units and points, planned against delivered.
   - Dropped and added units, each with its recorded reason.
   - Review rounds per unit.
3. **What known issues are handed over?**
   - Open findings raised in the run, with priority.
   - Units carried at the round cap.

It ends with the goal line ("met / partly met / missed", in one sentence) and a sign line.

**Appendix:** tokens by model, delegated tokens, DORA, calibration drift, and lesson
recurrence.

### What is missing to answer them honestly

- A plan snapshot keyed by run, so planned points survive resizing.
- A time forecast.
- Per-unit tokens and active time. Only 27 of 1,972 per-unit records carry either.
- A record for every review round.
- The model on every token stamp.

### Calibration back-test (area 3)

The test: forecast each run from the runs before it, over 24 runs.

| Forecaster | Geo-mean error | Within 2x |
| --- | --- | --- |
| 25,000 tokens x points (today) | 4.07x | 6 of 24 |
| Median of the last 5 runs | **2.03x** | **13 of 24** |

A rolling re-fit halves the error. Time cannot be fitted yet: run spans include idle time, so
active time must be measured first.

## The learning loop, redesigned (area 6)

**One committed store with one row per failure class, not per anecdote.** The fields are the
id, the class, a rule and a behaviour change, the injection points (plan, build or review), a
detection signal, the hits by run and unit, and a state (active, graduated or retired).

- **The retro "try" gives at most 3 items.**
  - An item that matches an existing class appends a hit instead of minting a lesson.
  - The "at least one lesson" gate becomes "at most three, each complete".
- **The review brief lists active class codes**, and a REJECT that matches one cites the code.
  At close, the hits are counted from the verdict ledger.
- **Two hits after recording graduate a lesson.**
  - A persona seat raises a CR for a check or a mechanism fix.
  - Until the check exists, the rule goes into the hard-rule block of the brief.
- **Five runs without a hit retire it.** This replaces validity dates and revalidation.
- **Calibration:** a rolling median of the current model's runs, written at close and read by
  the plan.
- **Precedent:** add Subject and Seat columns to `decisions.md`, and generalise the existing
  waiver lookup (`decisions.py waiver_for`) into `precedent`. A seat cites a prior ruling or
  records why it differs.
- **Collapse the 55 cross-project LL files into about 12 class rows.** The mutation-honesty
  class alone covers LL0050, LL0051, LL0053 and LL0054, plus five memory notes.

## Defects on the surviving core path

These would survive the rewrite, so the rebuild must fix them. They are listed here and not
filed one by one: each lands in the Sprint 1 unit that rebuilds its code.

| # | Defect | Where | Severity |
| --- | --- | --- | --- |
| 1 | `sign` seals whichever report is named and never re-checks the tree or compares it with the run's report | `sprint.py:9979, 10021` | High |
| 2 | A REJECT cannot be cleared by the documented re-review (the rejoinder fingerprint never matches) | `critic.py:709-748` | High |
| 3 | The review round cap is not enforced. The only live cap counts close attempts, and it shares `review.max_rounds` with the review cap under another default (4 vs 3) | `critic.py:2963`, `sprint.py:8138` | High |
| 4 | Calibration never runs: `measured_rate` refuses any history spanning two models, so plans always use the 25k seed | `retro.py:2053`, `sprint.py:274` | High |
| 5 | `transition set --verdict` accepts any word (`lgtm`) and skips the rules `critic record` enforces, writing the verdict before the transition that may refuse | `transition.py:2155-2216`, `critic.py:409` | Medium |
| 6 | Ledger and verify-report writes are non-atomic read-modify-write with no lock, so parallel reviewers lose rows | `critic.py:537-552`, `verify_ac.py:2042-2057` | Medium |
| 7 | An empty metadata field makes the reader and writer swallow the next line (`\s*` crosses the newline), which can overwrite body text | `sdlc_md.py:1063`, `transition.py:631` | Medium (latent) |
| 8 | `allocation_lock` fails open after 10 s, so two writers can mint the same id | `sdlc_md.py:2303-2327` | Medium |
| 9 | Re-running the close files a second report instead of replacing its own (this is how RPT0004 and RPT0005 both exist) | `sprint_report.py:4162` | Medium |
| 10 | A signed partial run is recorded as `stopped`, the label an abort gets. 17 of 18 archived `stopped` runs are signed partials | `sprint.py:9986, 5437` | Medium |
| 11 | Close attempts are counted before any refusal, so trivial refusals spend the cap and can lock out the step only close can clear | `sprint.py:9531` | Medium |
| 12 | Gates lint and test the working tree, not the staged index, so a partial stage commits untested bytes | `gate.py:266-300` | Medium |
| 13 | The batch pytest cache reports false reds for parametrised and nested-class selectors | `verify_ac.py:1601-1744` | Medium |
| 14 | `sprint call` forwards `--apply-signoff`, which `close` always refuses | `sprint.py:11687` | Low |
| 15 | `stop` without `--force` records the cause as `pending-decision` | `sprint.py:11167` | Low |
| 16 | Contradictions inside the process: the per-unit order in `help/sprint.md` cannot work (conformance before the critic), and five docs give five different loop lengths | docs | Low |

## Disclosure about the report just signed

**Unsupported claim in RPT0005.** Its goal verdict says Clauses 1-3 were delivered in full.
Clause 2 promised the report would show "the count of operator rulings against persona
rulings", but that count appears nowhere in RPT0005.md or RPT0005.json. The verdict note
overstates by one clause.

**Mislabelled and understated.** Defect 10 mislabels the run as "stopped", and the report
understates rework (1 round against a recorded 15).

The report stays sealed; this document is the correction on the record.

## The plan from here

### Sprint 1

- **Goal:** "A sprint runs start to finish on its own, learns from itself, and hands you one
  page." (17 words)
- **Scope:** rebuild the loop's spine around the lean process:
  - **Plan:** goal check, estimates in points, time and tokens, one approval.
  - **Review:** one reviewer, cap 2, carried issues. Fixes defects 2, 3, 5 and 6.
  - **Persona `rule` verb with precedent.**
  - **Close:** one command, the one-page report, 3-line retro and calibration. Fixes defects
    4, 9, 10 and 11.
  - **Sign:** checks the tree. Fixes defect 1.
  - **Capture:** per-unit and per-round time and tokens.
- **Bootstrap:** Sprint 1 has to run under today's machinery. The heaviest gates (plan review,
  test-plan review, mutation evidence, line coverage, two-role sign-off) are stood down through
  the existing config lane under one recorded decision, the precedent D0214 and D0249 set.

### Sprints 2 onwards

Run on the new loop. Work through the deletion ledger in bounded batches:

1. gates and hooks (the commit budget of 90 s first);
2. review and evidence surface;
3. reporting and records;
4. docs and config;
5. the learning store migration.

Each batch names its dependants before it deletes.

### Also

- **Release:** v6.0.0, a major version for consuming projects, with `migrate` carrying their
  config forward.
- **RFC0060:** folded in.
  - Kept: persona authority (D0232), the two-condition andon cord (D0233), no independence
    for persona rulings (D0235).
  - Superseded: the clause-checked goal (D0230, D0231).
  - EP0258 and EP0259 are re-scoped from this review.

## What the walkthrough on RUN-01M33WJ3 shows

**The target process on the same 5 bugs.**

- **Rounds:** recorded rounds were 3, 3, 2, 4 and 3 (`critic-evidence.md`).
- **Carried:** with a cap of 2, four units would have been carried as known issues with their
  round-3 and round-4 fixes filed as bugs. Those later rounds did find real defects, so this is
  the honest price of the cap: those defects move from hours of rounds to a visible,
  prioritised known-issues list.
- **The expected offset, not a measured one:** with no plan review, no mutant ledger and no
  coverage gate, far fewer surfaces generate a REJECT in the first place.

**Operator stops.**

- **Actual:** about 5 decisions in that run reached the operator (D0237-D0251).
- **Under the target:** plan approval and the signature. Every other question goes to a seat,
  and the coverage stand-down (D0249, D0251) never arises.

**The one-page report from data the run already holds.**

| Question | Answer from the run's data | Gap |
| --- | --- | --- |
| Points | Plan 13, actual 36 (RETRO0120) | - |
| Tokens | 4.77M forecast, 9.81M actual | - |
| Time | - | No forecast exists; the gap is Sprint 1's |
| Delivered to plan | 11 planned, 5 delivered, 6 stories dropped under D0250 | - |
| Known issues | BG0744 (High); BG0737-BG0743, CR0592, CR0593 | - |
