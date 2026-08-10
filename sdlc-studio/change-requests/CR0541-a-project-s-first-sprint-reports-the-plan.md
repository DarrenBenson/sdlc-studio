# CR-0541: a project's first sprint reports the plan-review requirement instead of refusing it, so a first-time user reaches a Done story unaided and meets the gate before it can matter

> **Status:** Complete
> **Decomposed-into:** EP0213
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/plan_review.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py
> **Evidence:** Measured through the shipped CLI on a greenfield fixture, 2026-08-09, during the v5 release-readiness sweep. `init.py run` on a clean repo, one ordinary story, then `transition.py requirements --id US0001 --status Done` returns `plan-review required (trigger: difficulty>=medium) - record an independent plan-review APPROVE (reviewer != plan author)`. Over this repository's own corpus of 1,171 units the routed bands split medium 821, low 177, high 167, trivial 6, so the medium-and-above trigger fires on roughly 70% of units - which for a project holding one story means it fires on the first one.
> **Date:** 2026-08-09
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Operator decision, 2026-08-09: soften the plan-review gate for a project's FIRST run only, then arm it. The gate is not the problem - it is the strongest evidence-backed feature in the release, and the N=5 bad-plan-propagates result is what justifies it. The problem is that it lands before the user has a reason to want it.

The rejected alternatives are recorded because both are worse. Keeping it as is preserves the gate and loses the adopter. Raising the default trigger to high would cut the gate from roughly 70% of units to about 14% by this repository's own band distribution - switching off the flagship v5 review feature for every project in order to fix the first ten minutes of one.

So the softening must be scoped to the first run and to nothing else. A project's first run reports the requirement, names what it will demand from the second run onwards, and does not refuse. From the second run the gate is armed and behaves exactly as it does today. An existing project upgrading to v5 has already had runs and is never softened - the concession is for a project with no run history, which is precisely the population that cannot have met the gate yet.

## Impact

Every new adopter. The first story a first-time user writes cannot reach Done without a second party reviewing its acceptance criteria against a spec the project may not have yet, and the only sanctioned way through is a `> **Plan-Review-Override:**` marker they have not been introduced to. A first run that cannot complete is the strongest argument a new user will ever have for abandoning the tool, and it is made before they have seen anything the tool is for.

## Acceptance Criteria

- [ ] A project with no closed run reports the plan-review requirement at the terminal transition and does not refuse, proven through the shipped `transition.py` on a greenfield fixture built by `init run`
- [ ] The same project's SECOND run refuses on the same story shape, proving the softening expires rather than persists (positive control on the same fixture, run history the only difference)
- [ ] A project that already has run history - the upgrading case - is unaffected byte-for-byte, and the test asserts the output is identical to the current behaviour
- [ ] The first-run report names the condition that arms the gate, and a test pins that the condition named is the one the gate actually reads rather than a restatement of it

## Recommendation

Option 1. The concession is bounded by a condition that expires on its own - a project acquires run history by using the tool - so nothing needs to be switched back on by hand and no config key is added that a project could leave in the loosened state. The report must name the run number that arms it, because a warning that does not say when it becomes a refusal trains the reader to ignore both.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-09 | sdlc-studio | Raised |
