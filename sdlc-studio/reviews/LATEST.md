# Unified Review - 2026-07-14 (close) - the sizing sprint: the loop measured itself, and the estimator failed

> **Review type:** Sprint-close review (required by the `--require-review` gate, CR0253)
> **Reviewer:** sdlc-studio; agent; v1
> **Date:** 2026-07-14
> **Triggered by:** the sprint close - review currency is a hard gate
> **Project version:** 4.1.0 released; unreleased work on `main` under a freeze until ~2026-07-21

## Headline

The sizing sprint is **complete - all 5 units** (CR0257, CR0258, BG0132, CR0259, CR0260), each
delivered by an instrumented subagent and verified independently through the public CLI before its
report was believed. RFC0034 is closed and **the breakdown step is now unavoidable**.

**The important result is a negative one: the token estimator is falsified.** The loop built to
measure the estimator did its job on its first honest run, and the thing it measured failed.

| unit | est (plan-time) | actual | ratio | tool-uses |
| --- | --- | --- | --- | --- |
| CR0257 | 67,400 | 97,863 | 0.69x | 45 |
| CR0258 | 77,000 | 107,623 | 0.72x | 36 |
| BG0132 | 73,400 | 129,957 | 0.56x | 58 |
| CR0259 | 67,400 | 144,711 | 0.47x | 60 |
| CR0260 | 67,400 | 162,204 | 0.42x | 81 |
| **BATCH** | **352,600** | **642,358** | **0.55x** | 280 |

`TOKENS_PER_COGNITIVE = 600` scored **1.09x in-sample** and **0.55x out-of-sample**. It under-forecasts
every unit, monotonically: the larger the job, the worse the miss. The previous coefficient (5,000)
over-forecast by 3.3x. Both were fitted to a single sprint; both failed the next one.

**The predictor is wrong, not the coefficient.** Cost correlates with tool-uses at r = 0.926 (~2,294
tokens each) and barely with the cognitive complexity of the files touched. Cost tracks WORK DONE, and
file complexity does not measure work done. But tool-uses is an OUTPUT, unknowable at plan time - so
this is not a better constant waiting to be fitted, it is evidence that the input we forecast from does
not carry the signal.

**The constants have NOT been changed.** Re-fitting to 11 points would repeat, for a third time, the
error this sprint documented twice. BG0133 must land first so a forecast is recorded at PLAN TIME;
only then can a sprint be judged against what was actually predicted.

## What the gates caught, unprompted

- **CR0260's breakdown gate, on its first run, refused three bugs filed that same day by our own
  filer** - all lacking `Affects`, because `file_finding.py` has no flag to record it (BG0136). The
  grooming gap the gate exists to close was being manufactured by our own tooling.
- It also caught two **false-parallel wave** pairs, one of which was CR0254/CR0260 - the CR that
  introduced the check, colliding with a sibling on `sprint.py`.
- The transition gate refused BG0132 to Fixed until a verification depth was recorded.
- The filer refused two hollow bugs.
- **BG0132 found 49 command-shaped `Verify:` lines across 18 artefacts** that nothing has ever
  executed - including one that PASSED on unrelated prose while the feature it claimed to check did
  not exist.

## Backlog rollup (9 non-terminal)

- **Bugs (5, all raised by this session's dogfooding):** BG0133 (High - the estimator cannot falsify
  itself), BG0136 (High - filer and planner disagree on what a complete artefact is), BG0134 (Medium -
  engagement floor fails open), BG0135 (Medium - reconcile blind to orphan index rows), BG0131 (Low)
- **CRs (4):** CR0252 (P1, spec refresh - still the outstanding P1), CR0254, CR0255, CR0256 (the
  RFC0033 audit workstream)

**Recommended next batch:** BG0133 first - it is the precondition for any future calibration decision,
and until it lands the velocity history is not evidence. Then BG0136, which closes the loop between
filer and planner. Then CR0252.

## Production state

v4.1.0 released and Latest on GitHub. **Freeze holds until ~2026-07-21.** All sprint work is on `main`
under `[Unreleased]`. No production release this week; forward-port to the installed copy for internal
testing only.

## For a fresh session

Start here, then `AGENTS.md`. The specs are still not a reliable product description until CR0252
lands - trust the CHANGELOG, `reference-*.md`, and the code. Read `RETRO0025` for the estimator's
falsification and why the constants were deliberately left alone; read LL0026 and LL0027, promoted this
sprint, before touching the calibration or adding another optional ceremony.
