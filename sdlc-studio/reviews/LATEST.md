# Unified Review - 2026-07-15 (close) - the sizing-completion sprint: the model works, the input was under-sized

> **Review type:** Sprint-close review (required by the `--require-review` gate, CR0253)
> **Reviewer:** sdlc-studio; agent; v1
> **Date:** 2026-07-15
> **Triggered by:** the sprint close - review currency is a hard gate
> **Project version:** 4.1.0 released; unreleased work on `main` under a freeze until ~2026-07-21

## Headline

**All 3 units delivered.** The RFC0038 size model is now complete in vocabulary: **T-shirts on requests
(CR/RFC/epic), points on delivery units (story/bug)**, and the forward-port is unblocked - every
evidence record now carries its project (CR0270), so a multi-project run is attributable.

**The forecast missed at 0.44x, and for the first time we walk into the close knowing why, with proof.**
A blind decomposition experiment this session settled it: two independent estimators, blind to cost,
decomposed the four points-model CRs into stories, and **sum of story points x the 25,000 seed predicted
the batch to 1.00x** (887,500 vs 887,704) where the single-shot CR points had missed by 0.56x. The
estimators agreed exactly on 3 of 4.

**So the four consecutive under-forecasts are not a fourth falsification of the estimator - they are
under-SIZING of the input.** CR0268 is the proof, appearing in both the sprint and the experiment: sized
2 at filing, decomposed to 6.5 by the blind estimators, and at 6.5 points it cost 23,679 tokens/point -
dead on the seed. **The rate was never wrong; my single-shot points were 1.75x too low.**

## The one caveat a fresh session must carry

This sprint's MEASURED rate in `VELOCITY.md` is **56,407 tokens/point - about 2.25x the seed - because
the points were under-sized.** It is a real record of what the sprint cost per recorded point, but the
points were casual single-shot estimates, so the rate is inflated. Do not re-fit the 25,000 seed to it.
The uncontaminated signal arrives once units are sized by decomposition (CR0271), which is the real
out-of-sample test of the rate.

## What went well

- **The gate caught its own author within one command.** CR0269 shipped "a bug carries points, not a
  T-shirt", and refused the very next bug this session filed with `--size`.
- **Verification by attack held all sprint:** the epic roll-up driven through reconcile (3+5+2 -> 10,
  bump -> 15), the project stamp proven on a fresh record and the cross-project pool refused, and the
  creator disagreement (BG0148) found by running both creators rather than reading either.
- The blind experiment is the strongest positive result of the whole estimation arc: decomposition does
  not just make Done checkable (BG0132), it makes the estimate accurate (LL0038).

## Backlog rollup (non-terminal)

- **The finale:** CR0271 (T-shirt L - the two-backlog gates: plan refuses a request, terminal status
  derived from children, UNDECOMPOSED drift kind). It is the last CR delivered whole - its own G1 gate
  makes CRs unplannable once it lands.
- **Bugs:** BG0148 (the creator disagreement - closes the size model), plus the earlier BG0142/0144/0145
  /0146 backlog.
- **Requests untouched this arc:** CR0254/0255/0256 (RFC0033 audit), the RFCs (0035 sprint report, 0036
  unattended multi-sprint, 0037 triage).

**Recommended next:** CR0271 as its solo finale, then forward-port a coherent whole (safe now - CR0270
stamps project) for the multi-project data run. BG0148 pairs naturally with CR0271 (both touch the
creators/gates).

## Production state

v4.1.0 released. Freeze holds until ~2026-07-21. All work on `main` under `[Unreleased]`. No production
release. **The forward-port is now safe to run in other repos** (project-stamped evidence), which is the
precondition for the operator's multi-project tuning run.

## For a fresh session

Start here, then `AGENTS.md`. Sizing is Fibonacci points on stories/bugs, T-shirts on CR/RFC/epic. Read
RETRO0028 and LL0038 (decomposition makes the estimate accurate) before touching the rate - and do NOT
re-fit the 25,000 seed to this sprint's inflated 56,407 measured rate; it reflects under-sized input, and
the honest test is the next decomposition-sized sprint.
