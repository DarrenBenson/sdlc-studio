# BG0449: the plan's grooming gate reported ok in enforcing blocking mode over four stories that carry the ungroomed banner and three placeholders each

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** amigo seat review of RUN-01KYPZ1G (independent, isolated worktrees); agent; v5.0.0
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

`sprint-plan.json` records the breakdown gate as `mode: enforce, blocking: true, ungroomed: [], ok: true`, and lists US0564, US0565, US0566 and US0567 among its groomed units. On disk each of those four is `Status: Draft`, carries three `{{role}}/{{capability}}/{{benefit}}` placeholders, and carries the literal banner `**Ungroomed - acceptance criteria are a grooming placeholder** - author each criterion and its Verify check against this story's slice while grooming, before it is planned to Done.` The gate is blind to a marker written into the very file it is gating, in the mode whose entire purpose is to refuse.

## Steps to Reproduce

Measured at d7a1ad8f, 2026-07-30:

```text
python3 -c "import json; b=json.load(open('sdlc-studio/.local/sprint-plan.json'))['breakdown']; print({k:b[k] for k in ('mode','blocking','ok')}, b['ungroomed'], 'US0564' in b['groomed'])"
{'mode': 'enforce', 'blocking': True, 'ok': True} [] True

grep -c '{{' sdlc-studio/stories/US0564-*.md   ->  3
grep -n 'Ungroomed' sdlc-studio/stories/US0564-*.md
21:> **Ungroomed - acceptance criteria are a grooming placeholder** ...
```

All four were subsequently DROPPED from the batch as ungroomed, which is how the gate's failure became visible: the drop reason states exactly the condition the gate declared absent. Found by the product amigo seat; re-measured by the author before filing.

## Proposed Fix

Read the marker. The template writes an unambiguous banner and the placeholder syntax is equally unambiguous - a gate that consults neither is checking something other than grooming. Detect BOTH, since either alone can be edited away: the banner is removed by hand during grooming, and the placeholders are what remain if someone deletes the banner without doing the work.

Pin it with a fixture story carrying the banner and placeholders, asserting the enforcing gate REFUSES and names the unit. The existing tests evidently assert the gate passes a groomed plan, which a gate that always passes also satisfies.

This is the recorded lesson about skeleton stories arriving from `refine --into` with placeholder ACs, one level up: the lesson says price the grooming, and this bug says the gate that should have refused to plan them instead certified them as groomed. Four stories and 15 points were planned into a sprint on that false green.

## Acceptance Criteria

- [ ] The behaviour described is corrected: `sprint-plan.json` records the breakdown gate as `mode: enforce, blocking: true, ungroomed: [], ok: true`, and lists US0564, US0565, US0566 and US0567 among...
- [ ] Following the recorded steps no longer reproduces the defect: Measured at d7a1ad8f, 2026-07-30: All four were subsequently DROPPED from the batch as ungroomed, which is how the gate's failure became visible: the drop...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | amigo seat review of RUN-01KYPZ1G (independent, isolated worktrees) | Filed |
