# Unified Review - 2026-07-14 (close) - the integrity sprint: the loop can now be falsified, and it falsified the estimator again

> **Review type:** Sprint-close review (required by the `--require-review` gate, CR0253)
> **Reviewer:** sdlc-studio; agent; v1
> **Date:** 2026-07-14
> **Triggered by:** the sprint close - review currency is a hard gate
> **Project version:** 4.1.0 released; unreleased work on `main` under a freeze until ~2026-07-21

## Headline

The integrity sprint is **complete - all 5 units** (BG0133, BG0134, BG0135, BG0136, CR0252), each
delivered by an instrumented subagent and verified independently through the public CLI before its
report was believed. **The only outstanding P1 is closed.**

**BG0133 is the one that matters.** The measurement loop can now be falsified. The forecast is
RECORDED at plan time with the constants that produced it, and `accuracy` reads that record - the
re-derivation path is deleted, not left as a fallback. Proven by attack: doubling both constants in
memory moves no recorded estimate. The 5.24x miss that CAUSED the recalibration, and had been erased
BY it, is restored to the history.

**And the loop immediately falsified the estimator a second time.**

| unit | est (plan-time) | actual | ratio |
| --- | --- | --- | --- |
| BG0134 | 50,000 | 71,935 | 0.70x |
| BG0135 | 81,200 | 173,804 | 0.47x |
| CR0252 | 80,000 | 205,534 | 0.39x |
| BG0136 | 73,400 | 234,091 | 0.31x |
| BG0133 | 63,800 | 217,139 | 0.29x |
| **BATCH** | **348,400** | **902,503** | **0.39x** |

The velocity history, honest for the first time:

| sprint | est | actual | ratio | sample |
| --- | --- | --- | --- | --- |
| RETRO0024 | 1,285,000 | 384,278 | 3.34x | in-sample (excluded) |
| RETRO0025 | 352,600 | 642,358 | 0.55x | out-of-sample |
| RETRO0026 | 348,400 | 902,503 | 0.39x | out-of-sample |

**Eleven of eleven units across two independent sprints, all missing in the same direction.** A model
that misses monotonically on every unit of two sprints is not mis-tuned - it is measuring the wrong
thing. The constants are UNCHANGED: re-fitting to 16 points would be the third repetition of the error
documented twice already.

**The open question is now the operator's, and it is not "what coefficient?"** It is **"is there a
plan-time predictor at all?"** Cost tracks work done (tool-uses, r = 0.926), and work done is unknowable
before the work is done. The live alternative is to drop the per-unit estimate and keep only the batch
history - two five-unit sprints cost 642k and 902k, which is a defensible basis for planning the next
one. A per-unit number that has never once been right is not.

## What the gates caught, unprompted

- CR0260's breakdown gate refused **three bugs our own filer had written that same day** - the filer had
  no `--affects` flag at all (BG0136), so it was manufacturing the gap the gate exists to close.
- BG0136's fix surfaced that `templates/core/cr.md` carried a **decoy `**Effort:**`** above the real one.
  `extract_field` takes the first match, so **every full-template CR had been unsized to the planner**
  whatever `--effort` said.
- BG0135's fix found **361 archived index rows link to the wrong depth** and 404 on GitHub (BG0137).
- The transition gate refused two bugs to Fixed until a verification depth was recorded.

## Backlog rollup (10 non-terminal)

- **Bugs (4):** BG0140 (High - the forecast log is gitignored, so BG0133's fix does not survive a
  clone), BG0139 (High - the model router scores a docs unit trivial with HIGH confidence, on the
  falsified predictor), BG0137 (Medium - 361 dead archive links), BG0138 (Low)
- **CRs (4):** CR0261 (P2 - record which model delivered each unit), CR0254, CR0255, CR0256 (the
  RFC0033 audit workstream)
- **RFCs (2, Proposed):** RFC0035 (the sprint report), RFC0036 (unattended multi-sprint: a rolling
  policy, not a frozen queue)

**Recommended next batch:** BG0140 first - until the forecast log survives a clone, the evidence the
whole loop rests on exists on one machine. Then BG0139 (do not enable routing before it lands) and
CR0261, which BG0140 unblocks.

## Production state

v4.1.0 released and Latest on GitHub. **Freeze holds until ~2026-07-21.** All sprint work is on `main`
under `[Unreleased]`. No production release this week; forward-port to the installed copy for internal
testing only.

## For a fresh session

Start here, then `AGENTS.md`. **The specs are trustworthy again** (CR0252) - PRD, TRD and TSD are at
4.1.0 with five new ADRs. Read `RETRO0026` for the second falsification and why the constants were
deliberately left alone, and LL0026-LL0029 before touching the calibration, the router, or adding
another optional ceremony.
