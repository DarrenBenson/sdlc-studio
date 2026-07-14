# BG0147: The dead complexity signal still orders the batch: CR0262 removed it from the forecast and left it as the WSJF tie-breaker

> **Status:** Fixed
> **Severity:** Medium
> **Effort:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Verification depth:** functional - the dead `max_cognitive` tie-break is deleted from _rank_key (grep returns zero), and equal-WSJF units now fall to id order. Verified through the public plan CLI: ordering is by WSJF then id, never by the complexity of the files touched.
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

CR0262 established that `max_cognitive` scores r = +0.03 against measured cost and r = -0.001 against measured work, and removed it from the token forecast on that basis. It is still the ORDERING signal. `_rank_key` falls back to `it["complexity"]` whenever the review seats have not scored a unit - which is the normal case - so the running order within a priority band is decided by a number with no demonstrated meaning.

The docstring states the rationale plainly: "the cognitive complexity of the files a unit will touch breaks ties within a priority, so the smaller blast-radius job goes first". The evidence contradicts it. Complexity does not measure the size of the job; it measures the complication of the FILE the job happens to touch, which is why a one-line fix in a large module scores maximum and a whole docs rewrite scores zero.

It is not very harmful - priority remains the dominant axis, and a wrong tie-break within a band costs order, not correctness. But it is exactly the false authority this project keeps hunting: a number that LOOKS meaningful, is not, and quietly makes decisions while a docstring vouches for it. Shortest-job-first is a sound scheduling heuristic; it just needs a size signal that is real.

And one is already there. The declared human Effort scores r = 0.35 against cost - an order of magnitude better than complexity, already parsed, and already the WSJF denominator (CR0257). The tie-break should use the size signal the planner already trusts everywhere else, or it should be dropped entirely and fall to id order, which is at least honestly arbitrary.

## Steps to Reproduce

1. Read sprint.py `_rank_key`: when a unit has no seat-derived WSJF score, the key is (`priority_weight`, complexity, id). 2. Plan any batch the seats have not scored - the normal case. 3. The order within each priority band is set by `max_cognitive`, the signal CR0262 removed from the forecast for scoring r = +0.03 against cost. 4. Read the module docstring: it still claims the tie-break puts "the smaller blast-radius job" first.

## Proposed Fix

Use the declared Effort as the tie-break size (falling back to id order when it is absent or unknown), so the planner orders by the one size signal it has evidence for and already relies on for WSJF. Correct the docstring: it currently vouches for a claim the data refutes. If Effort is judged too weak to order by, drop the tie-break and fall to id - arbitrary and honest beats meaningful-looking and arbitrary. Either way, an `unknown` Effort must not be coerced into a number (CR0263).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Filed |
