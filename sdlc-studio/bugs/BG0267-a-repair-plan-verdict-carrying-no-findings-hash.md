# BG0267: A repair-plan verdict carrying no findings-hash token satisfies the pin check vacuously

> **Status:** Fixed
> **Verification depth:** functional (unit: a verdict with no findings-hash token now fails the pin check instead of satisfying it vacuously; mutation-proven at the call site)
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/repair_plan.py,.claude/skills/sdlc-studio/scripts/tests/test_repair_plan.py
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Found by the closing adversarial review of RUN-01KY5Y3W. `plan_reviewed` guards US0313's pin with `if m and m.group(1) != current` (`repair_plan.py` around line 275): a plan-review verdict that carries NO `findings-hash=` token passes the pinned-to-current-findings check vacuously, because the `m` guard short-circuits. The shipped `review_repair_plan` always writes the token, so this is not reachable through the public API - but a verdict recorded via `critic.record_verdict` directly, or a hand-edited verdict row, would satisfy the pin without being pinned. It is the same has-less-verdict back-compat hole `plan_review._has_independent_plan_approval` carries, and the same fix applies: decide deliberately whether an untokened verdict is honoured or refused, rather than passing by omission. Latent, not exploitable on the shipped path, which is why it is Low.

## Steps to Reproduce

1. Record a plan-review APPROVE for a repair plan via `critic.record_verdict` directly, with an issues field carrying no `findings-hash=` token. 2. Call `repair_plan.plan_reviewed.` Observed: it returns ok=True even though nothing pins the verdict to the plan's current findings. Expected: an untokened verdict is either refused as unpinned, or the decision to honour it is explicit and tested.

## Proposed Fix

Decide the untokened case deliberately in `plan_reviewed`: either treat a verdict with no findings-hash as NOT pinned (return ok False, matching US0313's intent that a verdict answers a specific finding set), or, if back-compat honouring is wanted, make that an explicit branch with its own test. Do not let it pass by the `m and` short-circuit.

## Acceptance Criteria

### AC1: an untokened plan-review verdict is decided deliberately, not by short-circuit

- **Given** a plan-review APPROVE recorded with no `findings-hash=` token in its issues field
- **When** `repair_plan.plan_reviewed` evaluates it
- **Then** the untokened case takes an explicit branch with a stated decision, rather than passing because the match guard short-circuited
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_repair_plan.py::UntokenedVerdictPinTests::test_an_untokened_verdict_is_not_treated_as_pinned

### AC2: a tokened verdict pinned to the current findings still passes, unregressed

- **Given** a plan-review APPROVE carrying a `findings-hash=` token equal to the plan's current findings
- **When** `plan_reviewed` evaluates it
- **Then** it passes exactly as before, so the fix narrows only the untokened hole
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_repair_plan.py::UntokenedVerdictPinTests::test_a_correctly_pinned_verdict_still_passes

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Filed |
| 2026-07-24 | sdlc-studio | Fixed: `plan_reviewed` takes an explicit untokened branch and refuses an unpinned verdict, naming the missing `findings-hash`. Both ACs verified by `UntokenedVerdictPinTests`; two mutants killed (restore the short-circuit; refuse every verdict). |
