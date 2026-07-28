# BG0376: Five stories' caller criteria are verified by a test class that never reads the story, so the criterion cannot fail

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** High
> **Points:** 3
> **Affects:** sdlc-studio/stories/US0508-a-lane-refuses-to-start-on-a-unit.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (independent re-review of 343da768, run wf_b62b2ed2); agent; skill v5.0.0

## Summary

Acceptance criteria added at review to close the caller-naming finding on US0508, US0509, US0510, US0512 and US0520 each state that the caller check runs over THIS unit and that its consuming call site resolves. Each is verified by a pre-existing test class over synthetic temporary fixtures which never reads the story it is attached to, so the criterion is green whatever the story says. An independent reviewer deleted the Caller declaration from US0508: the caller check immediately reported caller-unnamed and exited 1, while the story's own criterion still passed. The verifier also does not run the at-scale test the repair added, so that test is referenced by no criterion at all.

## Steps to Reproduce

Independent re-review of 343da768. Remove the Caller bullet from US0508, run the caller check over the unit (exit 1), then run the criterion's own verifier: it passes. The criterion asserts a property of the story and is proven by a fixture that has never seen the story.

## Proposed Fix

Point each of the five criteria at a check that can fail on the unit - the caller check invoked against that unit id, which exits non-zero on a finding - rather than at a synthetic class. Where a pytest selector is wanted instead, add a test that reads the actual story file and asserts its declaration resolves.

## Acceptance Criteria

No acceptance criterion could be derived from this finding's evidence: `steps` carries fewer than 5 words of substance, so nothing here states what fixed would look like. Whoever picks this up agrees the contract with the author before starting - this is a stated gap, not a criterion to tick.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 (independent re-review of 343da768, run wf_b62b2ed2) | Filed |
| 2026-07-28 | Claude Opus 5 | Fixed: the five criteria now run `critic.py caller-check --unit <id>`, which exits 1 when the Caller declaration is removed - the reviewer's mutation now kills them. |
