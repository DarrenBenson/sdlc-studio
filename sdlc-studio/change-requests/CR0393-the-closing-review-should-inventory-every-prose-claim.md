# CR-0393: The closing review should inventory every prose CLAIM against the diff as its FIRST pass, not discover them last

> **Status:** In Progress
> **Decomposed-into:** EP0109
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/reference-review.md,.claude/skills/sdlc-studio/templates/audit-profiles/test.md,.claude/skills/sdlc-studio/scripts/critic.py
> **Date:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Nine consecutive closing reviews on this project have had the same surviving MAJOR class: prose asserting a property the code does not have. RUN-01KY3MFX made it measurable. Across five rounds and 23 MAJORs, the great majority were claims rather than logic - a Resolution saying mutation-proven when the mutants never reached the lane; a docstring saying two sources are never silently substituted while one branch did exactly that; a comment saying an unrelated negation cannot launder an assertion when it can; a CLI sentence describing a guard it contradicted, wrong five times running; a test comment asserting two implementations cannot diverge while its shape list had been drawn from the families where they agree by construction. Rounds 4 and 5 found one narrow code defect each and three false claims each. Reviewers reach these findings LAST, after reading the logic, which is the most expensive order: the claims are the cheapest thing in the diff to check and the likeliest to be wrong. The reviewer of round 3 said so unprompted, recommending the review read Resolutions against the diff as a first pass rather than a last one. Note the structural reason this class persists: a Resolution is written after the work, by the author, to justify what they just did, and it is the one artefact in the repo that no test can fail.

## Impact

Every closing review, and every consuming project that adopts the review model. The cost today is paid in review ROUNDS - the most expensive currency this project has, at roughly 200,000 tokens each - because a false claim found in round 4 could have been found in round 1 by reading the same sentence.

## Acceptance Criteria

- [ ] The reviewer brief directs an explicit first pass that enumerates every assertion in the diff's Resolutions, docstrings, comments and CHANGELOG entries, and marks each TRUE, FALSE or UNVERIFIABLE against the code.
- [ ] A claim that cannot be checked mechanically is reported as UNVERIFIABLE rather than assumed true, so the reader can see how much of the prose rests on trust.
- [ ] The pass runs BEFORE the logic review and its findings are reported separately, so a round that finds only prose defects is visibly a different kind of round from one that finds logic defects.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Raised |
