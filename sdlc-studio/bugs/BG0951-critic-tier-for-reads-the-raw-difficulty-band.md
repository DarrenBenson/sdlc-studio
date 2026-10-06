# BG0951: `critic.tier_for` reads the raw difficulty band and skips every critic-role policy `route.pick` applies, so code units get a light review the routing policy says should be medium

> **Status:** Won't Fix
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/route.py, .claude/skills/sdlc-studio/scripts/tests/test_tier_for_critic_policy.py
> **Evidence:** Found migrating a consuming project from skill 2.4.1 to the installed 6.1.0 on 2026-10-06; reproduced against sdlc-studio main at aa19a2e3. US0601 critic verdict REJECT recorded in the consuming project's sdlc-studio/reviews/critic-verdicts.md; filed there as BG0491.
> **Created:** 2026-10-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-06T12:35:20Z

## Summary

`tier_for` (critic.py:2334) derives the review tier from `route.estimate(...)['difficulty_band']` through `BAND_TIER`, where `trivial` and `low` map to `light`. `route.pick(role='critic')` (route.py:209) is where the routing policy lives: kind floors, the high-risk-band security floor, the low-confidence upward bump, and the critic rule - never smaller than the author, and **medium floor for code units**. `tier_for` calls none of it, so for a code-touching unit the brief can come out light while `pick` for the same unit and role says medium.

Concrete case: the consuming project's US0601 (an authorisation change - per-agent bearer ownership checks on two REST routes). `route.estimate` gives band `low`, confidence `low`; `critic.tier_for` gives `light`; `route.pick(role='critic')` gives tier `medium` with adjustment `confidence:low`. Overridden to full, the independent review ran 14 mutants and returned REJECT with three blocking defects (an AC ticked Verified that the suite contradicts, a false published contract, an unpinned guard that kept a stale binding from widening access). Whether a light pass would have caught them is unknown; what is certain is that the tier the brief chose ignored the policy written for exactly this role.

`tier_for`'s own docstring argues 'the cost of a needless light one is a defect that ships' and fails towards full on an unknown band - but a low-confidence band is treated as certain.

## Steps to Reproduce

From a consuming project with a low-band code unit (e.g. the consuming project's US0601):

```bash
python3 -c "import sys; sys.path.insert(0,'<skill>/scripts'); from pathlib import Path; import route, critic; from lib import sdlc_md; r=Path('.'); f=sdlc_md.find_by_id(r,'US0601')[0]; print(route.estimate(r,f)['difficulty_band'], route.estimate(r,f)['confidence']); print(critic.tier_for(r,'US0601')); print(route.pick(r,f,role='critic')['tier'], route.pick(r,f,role='critic')['adjustments'])"
```

Observed: `low low` / `light` / `medium ['confidence:low']`.

## Proposed Fix

Derive the review tier from `route.pick(..., role='critic')` (or a shared function both call) so the critic floors, the security floor and the low-confidence bump apply; at minimum, a low-confidence band and a code-touching unit must not tier light.

## Acceptance Criteria

- [ ] **AC1** For a code-touching unit, `tier_for` never returns `light` when `route.pick(role='critic')` returns medium or above, shown by a test
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_tier_for_critic_policy.py -k code_unit_not_light
- [ ] **AC2** A low-confidence difficulty band tiers the review no lighter than `pick` does for the critic role
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_tier_for_critic_policy.py -k low_confidence
- [ ] **AC3** The security floor applied by `pick` reaches the review tier
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_tier_for_critic_policy.py -k security_floor

## Triage

Won't Fix: the premise compares two different tiers, and the raiser agrees.

- `route.pick`'s tier (tiny/small/medium/large/xlarge, route.py:55) is a model-size
  recommendation, advisory, read by no gate. "Medium floor for code units" means the reviewer
  gets at least a medium model; it says nothing about review depth.
- `critic.tier_for`'s tier (full/light, critic.py:49) is review depth. `BAND_TIER` is declared
  once with its reason (US0641, CR0510), and an explicit `--tier` is recorded apart from a derived
  one so the derivation can be judged against the reviews it produced. The US0601 `--tier full`
  override is that evidence, working as designed.
- AC1 as written would floor every code-touching unit at full and end the light pass for code,
  which is a policy change, not a repair.
- What remains is a judgement call, not a broken guarantee: whether a low-confidence band (or an
  authorisation change) should earn the full review. One case with no control does not carry it;
  the explicit-tier ledger is where the evidence would accumulate. Raise it as a CR if that
  ledger shows light-tier misses.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-06 | Claude Opus 5.5 | Filed |
| 2026-10-06 | Claude Opus 5.5 (triage) | Won't Fix: model-size tier read as review depth; raiser concurs |
| 2026-10-06 | Claude Opus 5.5 (triage) | Consuming-project name generalised for the neutrality lane |
