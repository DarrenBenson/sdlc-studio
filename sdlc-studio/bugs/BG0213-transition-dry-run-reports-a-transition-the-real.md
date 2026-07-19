# BG0213: transition --dry-run reports a transition the real run refuses, so the one pre-flight an agent has lies

> **Status:** Fixed
> **Verification depth:** functional (dry-run and real run now agree on the same input; both branches mutation-killed; verified live on BG0212)
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Created:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

transition.py set --dry-run does not run the transition gates. A bug with no parseable Verification depth field is reported as 'would set BG0001 Open -> Fixed', while the real run BLOCKS with 'no parseable Verification depth field; Fixed requires functional+'. The dry-run and the real run disagree about the same transition. This is worse than having no dry-run: a dry-run exists so an agent can learn the requirements BEFORE doing the work, and this one actively asserts the opposite, so the requirement is still met as a refusal after the work is done. Found while grooming US0267, whose whole subject is naming a unit's required fields ahead of its terminal transition - the mechanism that should carry that answer is the one giving the wrong one. Same false-completeness class as BG0207: the output is not merely incomplete, it is confidently wrong.

## Steps to Reproduce

In a scratch workspace, create sdlc-studio/bugs/BG0001-x.md with Status Open, Severity Low, Points 2 and NO 'Verification depth' line, plus a matching _index.md row. Then: python3 transition.py --root . set --id BG0001 --status Fixed --dry-run  -> prints 'would set BG0001 Open -> Fixed'. And: python3 transition.py --root . set --id BG0001 --status Fixed  -> prints 'blocked ... no parseable Verification depth field; Fixed requires functional+', and the file stays Open. The two answers contradict each other.

## Proposed Fix

Run the same gate evaluation on the dry-run path as on the real path, and report the refusals it would hit, changing nothing. The dry-run's answer must match the real run's answer for the same inputs; the only difference should be whether the write happens. Add a regression test asserting that a unit failing a terminal-transition requirement is reported as blocked under --dry-run too.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Filed |
