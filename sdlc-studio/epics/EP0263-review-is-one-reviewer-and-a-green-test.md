# EP0263: Review is one reviewer and a green test: the review and evidence surface is deleted

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** XL

## Summary

Sprint 3 of the back-to-basics programme, part two (deletion batch 2). Deletes plan review, test-plan review, the repair ledger, the evidence and sprint-review ledgers, per-unit two-role sign-off, verification depth tiers, the mutation register and evidence-drift lane (mutation stays as opt-in run), and brief provenance; line coverage becomes opt-in. Yield evidence: 242 of 255 plan-review rejections argued over test apparatus, 636 of 637 depth tiers read functional, 1,033 of 1,043 mutants killed. migrate carries consuming projects' config forward; existing ledgers stay as frozen history.

Groomed for Sprint 4 on 2026-09-25 from the engineering-seat readiness review: 21 units totalling 102 points, not 67. US0910, US0920 and US0921 were split (their second halves are US0934, US0935 and US0936). File-disjointness and the measured dependency order give 13 build waves of at most two units: (1) US0934, US0921; (2) US0911, US0910; (3) US0916; (4) US0913, US0920; (5) US0909, US0917; (6) US0915, US0935; (7) US0912, US0914; (8) US0936, US0922; (9) US0918; (10) US0919; (11) US0923; (12) US0924, US0925; (13) US0926. Each wave merges one unit at a time, reruns `docgen.py surface` and runs the full suite before the next opens. Sprint 4 takes waves 1-4 (7 units, 27 points) beside CR0594, extending to wave 5 if velocity allows.

## Story Breakdown

- [x] [US0909: A story reaches In Progress and Done without a plan review](../stories/US0909-a-story-reaches-in-progress-and-done-without.md)
- [x] [US0910: A bug reaches Fixed without a verification depth tier](../stories/US0910-a-bug-reaches-fixed-without-a-verification-depth.md)
- [x] [US0911: A unit reaches Done without a test plan or a falsifiability probe](../stories/US0911-a-unit-reaches-done-without-a-test-plan.md)
- [x] [US0912: The test-plan tooling is gone and an old Test Plan section is inert](../stories/US0912-the-test-plan-tooling-is-gone-and-an.md)
- [x] [US0913: A repair closes without a reviewed repair plan](../stories/US0913-a-repair-closes-without-a-reviewed-repair-plan.md)
- [x] [US0914: A standing REJECT clears only by a round-2 APPROVE or by carrying the unit](../stories/US0914-a-standing-reject-clears-only-by-a-round.md)
- [x] [US0915: A review verdict has one phase: delivery](../stories/US0915-a-review-verdict-has-one-phase-delivery.md)
- [x] [US0916: A story reaches Done without a per-unit reviewer-of-record sign-off](../stories/US0916-a-story-reaches-done-without-a-per-unit.md)
- [x] [US0917: The operator's signature seals the run without a per-unit sign-off row](../stories/US0917-the-operator-s-signature-seals-the-run-without.md)
- [x] [US0918: One verdict ledger decides whether a unit was reviewed](../stories/US0918-one-verdict-ledger-decides-whether-a-unit-was.md)
- [x] [US0919: Sign-off is the operator's one signature and the per-unit sign-off verbs are gone](../stories/US0919-sign-off-is-the-operator-s-one-signature.md)
- [x] [US0920: A repair reaches Fixed without registered mutation evidence](../stories/US0920-a-repair-reaches-fixed-without-registered-mutation-evidence.md)
- [x] [US0921: Mutation testing is an opt-in run with a yield and nothing more](../stories/US0921-mutation-testing-is-an-opt-in-run-with.md)
- [x] [US0922: Line coverage is measured only when a project opts in](../stories/US0922-line-coverage-is-measured-only-when-a-project.md)
- [x] [US0923: A review verdict records without brief provenance](../stories/US0923-a-review-verdict-records-without-brief-provenance.md)
- [ ] [US0924: The shipped docs teach only the surviving review path](../stories/US0924-the-shipped-docs-teach-only-the-surviving-review.md)
- [ ] [US0925: An upgrading project's config carries forward without the retired review keys](../stories/US0925-an-upgrading-project-s-config-carries-forward-without.md)
- [ ] [US0926: This repository runs on the shipped defaults with no stand-down keys](../stories/US0926-this-repository-runs-on-the-shipped-defaults-with.md)
- [x] [US0934: A bug reaches Fixed without a depth gate, and the retired --depth flags are refused](../stories/US0934-a-bug-reaches-fixed-without-a-depth-gate.md)
- [x] [US0935: A repair reaches Fixed without the mutation-evidence gate, survivor filing or evidence mode](../stories/US0935-a-repair-reaches-fixed-without-the-mutation-evidence.md)
- [x] [US0936: The mutation ledger verbs are retired and a mutation run reports its yield only](../stories/US0936-the-mutation-ledger-verbs-are-retired-and-a.md)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-25 | Engineering seat | Summary notes the re-size to 102 points over 21 units and the 13 build waves from the Sprint 4 readiness review |
