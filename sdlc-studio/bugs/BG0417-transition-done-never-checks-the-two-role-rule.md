# BG0417: transition -> Done never checks the two-role rule: the verb that writes the status the Definition of Done defines a bar for does not consult that bar, and only a later gate run reports it

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py
> **Evidence:** US0479 carries an independent reviewer-of-record sign-off and NO adversarial evidence: `critic.evidence_for` returns nothing and no sprint-level review covers it. `conformance` correctly reports the evidence half unmet. `transition.py set US0479 Done --dry-run` prints `would set US0479 Review -> Done`. `grep -n 'conformance' transition.py` returns one comment and no call; `grep -n 'two_role' transition.py` returns nothing. The same holds for US0531, US0554 and US0559 - all ten units of EP0189, EP0181 and EP0172.
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The Definition of Done states the Story bar as three clauses, one of which is `The adversarial pass is recorded as evidence and the reviewer of record has signed off [check: review.two-role]`. `conformance.py` implements that clause properly: past `review.two_role_after`, a Done unit needs both an evidence half (a per-unit adversarial pass, or a sprint-level review covering it) and an independent sign-off half, and it reports each unmet half by name.

`transition.py` - the verb that actually writes `Status: Done` - never consults it. It gates a story's Done on the AC-verify result and nothing else. There is no call to conformance, no read of `review.two_role_after`, and no reference to the evidence half anywhere in the module.

So the bar is enforced by a lane that runs later, over a status a different tool has already written. A unit can be moved to Done with no independent review whatsoever, and the only trace is a conformance report someone has to run and read. Nothing at the moment of the write says no.

This is the cause of BG0350, which is filed as the symptom: 25 Done stories carrying no independent critic verdict, waived under D0074 rather than cleared. They did not slip past a gate; the gate they are said to have passed was never asked. The same mechanism means the ten units of EP0189, EP0181 and EP0172 - which have a genuine operator sign-off and no adversarial pass at all - are one `transition set` away from Done.

It is also the exact shape this project files bugs about most often, and which its own carried lessons name twice: a guard that answers a narrower question than it claims, and a rule stated in one place and enforced in another that the first place never calls.

## Steps to Reproduce

1. Pick a unit past `review.two_role_after` with a sign-off and no adversarial evidence - US0479 is one today.
2. Confirm the two halves: `critic.evidence_for(root, 'US0479')` is falsy, `critic.signoff_for(root, 'US0479')` is truthy.
3. Run `transition.py set US0479 Done --dry-run`. It prints `would set US0479 Review -> Done`.
4. `grep -n 'conformance\|two_role' .claude/skills/sdlc-studio/scripts/transition.py` - one unrelated comment, no call, no config read.

## Proposed Fix

1. **The verb enforces the bar it writes.** `transition -> Done` for a unit past `review.two_role_after` refuses unless both halves hold, reusing `conformance`'s existing predicate rather than reimplementing it - a second copy of the two-role rule is a second place for it to drift.
2. **The refusal names WHICH half is missing**, in the vocabulary conformance already uses, so the remedy is obvious from the message: an absent adversarial pass and an absent sign-off need different actions from different people.
3. **`--force` stays available and stays recorded.** The existing force-override machinery already writes what was waived to the artefact and the revision row; a two-role bypass must be at least as visible.
4. **The existing waiver is re-examined.** D0074 waived 25 units against a gate that was never asked. Whether they are re-reviewed or the waiver is restated with the real reason is a judgement, but it must not stay recorded as 'waived past a gate' when no gate ran.
5. A test moves a past-cutoff unit with a sign-off and no evidence to Done and asserts the REFUSAL, and a second asserts a pre-cutoff unit is unaffected - the rule is forward-only by design.

## Acceptance Criteria

- [ ] `transition -> Done` refuses a unit past `review.two_role_after` that is missing either two-role half, reusing conformance's predicate rather than a second copy of the rule.
- [ ] The refusal names which half is unmet, using the same vocabulary conformance reports, so the remedy and its owner are clear from the message.
- [ ] `--force` can still bypass it and records what was waived on the artefact and the revision row, exactly as the existing force-override machinery does.
- [ ] A pre-cutoff unit and a project with no `review.two_role_after` configured are byte-for-byte unaffected - the rule is forward-only.
- [ ] A test transitions a past-cutoff unit that has a sign-off and NO evidence and asserts the refusal; the mutant that drops the evidence half must redden it.
- [ ] The D0074 waiver is restated against what actually happened, or the units behind it are re-reviewed - it must not read as 'waived past a gate' when no gate was ever asked.

## Impact

The two-role rule is this project's central quality claim and the thing it asks consuming projects to adopt: whoever wrote the change never records its sign-off, and an adversarial pass by a fresh context is evidence. A consuming project inherits a Definition of Done asserting that bar and a transition verb that does not apply it.

The practical effect here is that Done means less than the documents say it means, and nobody reading a Done unit can tell which kind of Done it is without running a separate lane. Twenty-five units are already in that state. Ten more are one command away.

The gate does catch it eventually, so this is not a silent hole in the same class as a fail-open release guard. It is worse in one specific way: it puts the true status and the recorded status out of step for however long it takes someone to run the lane, and the recorded status is what every other reader trusts.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Filed |
