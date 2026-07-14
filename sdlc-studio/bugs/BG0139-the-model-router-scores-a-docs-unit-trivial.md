# BG0139: The model router scores a docs unit trivial with high confidence: its dominant signal is the predictor falsified today

> **Status:** Won't Fix
> **Severity:** High
> **Effort:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/route.py, .claude/skills/sdlc-studio/scripts/complexity.py
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

route.py recommends a model tier from a difficulty score whose heaviest subscores are code complexity (complexity.py blast-radius cognitive) and churn-weighted risk. That is the same predictor the token forecast used, and it was falsified out-of-sample today (0.55x over 11 units, missing monotonically - see RETRO0025). Measured against the 15 units now carrying real telemetry, the difficulty score correlates with actual cost at r = 0.13. The failure is structural, not a tuning error: a markdown file has no cognitive complexity, so a non-code unit scores near zero on the two dominant subscores and comes out trivial. The router is blind to difficulty in non-code work. CR0252 - the P1 spec refresh across three documents, which added five ADRs and found eight substantive errors in the specs - scored 14 (trivial), confidence HIGH, and cost 205,534 tokens: the second most expensive unit measured. With routing.enabled it would have been sent to the SMALLEST model, without hedging. The missing-signal doctrine that exists to prevent exactly this (unknown difficulty defaults to 0.5, never 0; low confidence bumps the tier UP) does not fire, because the signals did not go MISSING - they resolved, to zero. A resolved-but-meaningless signal is more dangerous than an absent one, because the confidence stays high. Routing is advisory and disabled by default, which is why this is not Critical.

## Steps to Reproduce

1. python3 scripts/route.py estimate --unit sdlc-studio/change-requests/CR0252-*.md --format json 2. Read: `difficulty_score` 14, `difficulty_band` trivial, confidence high; subscores code and risk near 0 because the unit touches prd.md/trd.md/tsd.md. 3. Compare with the recorded actual in .local/telemetry.jsonl: 205,534 tokens, the second-largest unit measured. 4. Repeat across the 15 units with telemetry: r(`difficulty_score`, actual tokens) = 0.13, and the trivial band contains both the cheapest unit (46,359) and the second dearest (205,534).

## Proposed Fix

Do not enable routing on this score. Three things, in order. (a) Treat a resolved-but-inapplicable signal as MISSING, not as zero: a unit whose Affects names no code file has no code subscore, so the code and risk subscores must be recorded in missing (default 0.5) and drop confidence, which lifts the tier - the doctrine already written in the module docstring, simply not reached. That alone would stop a docs unit reading as trivial with high confidence. (b) Add a signal that carries non-code difficulty. The declared human Effort (S/M/L) is the obvious candidate: it is the one estimate a person actually recorded, it exists on every unit since CR0257, and CR0252 declares L. (c) Validate the router the way the forecast was validated - against measured actuals, out-of-sample, before anyone trusts it. The lesson of this week is that a plausible predictor that nobody has tested against outcomes is a guess wearing a number.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Filed |

## Resolution: DUPLICATE - subsumed by CR0262 (2026-07-14)

Closed without separate work, and not to shrink a sprint. This bug and CR0262 are the same change,
filed twice, hours apart, by the same agent.

- BG0139's fix **(a)** - "treat a resolved-but-inapplicable signal as MISSING, not as zero" - is
  **CR0262 AC4**, verbatim.
- BG0139's fix **(b)** - "add a signal that carries non-code difficulty; the declared Effort is the
  obvious candidate" - is **CR0262 AC1**.
- BG0139's fix **(c)** - "validate the router against measured actuals, out-of-sample, before anyone
  trusts it" - is **CR0262 AC2**.

Both bugs are the same root cause: the router and the forecast are dominated by the SAME inert signal
(`max_cognitive`, r = -0.006 against cost). Fixing the signal in one place fixes both consumers, and
splitting it across two artefacts would split the acceptance criteria for one change so that neither is
complete on its own - and would dispatch two agents concurrently into `route.py` and `complexity.py`.

**The routing warning stands and is carried by CR0262: do not enable `routing.enabled` until the seed
is rebuilt and validated out-of-sample.**

It was caught only because CR0260's shared-file clustering put the two in one collision cluster. That
the tooling has no duplicate detection at filing is now **CR0264**.
