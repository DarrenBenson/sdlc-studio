# CR-0536: the spec documents do not learn about a tool that ships, and the guards meant to catch that cannot fail

> **Status:** In Progress
> **Decomposed-into:** EP0234
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/spec_guard.py, .claude/skills/sdlc-studio/scripts/tests/test_spec_guard.py, tools/check_spec_claims.py, sdlc-studio/trd.md, sdlc-studio/tsd.md, tools/tests/test_check_spec_claims.py
> **Evidence:** RUN-01KZCAJX, 2026-08-06. `grep -ci 'testplan derive|corpus-scan|_EDIT_VERBS|test_plan_after' sdlc-studio/trd.md sdlc-studio/tsd.md` -> 0 and 0, for four surfaces shipped in the same run. BG0457 records the four existing spec-agreement guards and the mutations each survives. The Revision-History-satisfies-the-guard defect recurred independently on US0567 in this same run and had to be designed out by slicing the rule's own passage.
> **Date:** 2026-08-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson; human; operator proposal at the RUN-01KZCAJX delivery
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

A verb can ship with a new refusal and no spec document notices. RUN-01KZCAJX shipped `verify_ac testplan derive`, `verify_ac corpus-scan`, an edit-verb vocabulary that refuses input, and the `review.test_plan_after` gate. `grep` over `trd.md` and `tsd.md` finds ZERO mentions of any of them. The TSD is the document a sprint plan reads to derive its test strategy, so the strategy is derived from a document that does not know what the tooling now refuses.

The obvious fix - write them into the TRD - is the wrong one, and BG0457 is the reason. Four spec-agreement guards already exist to keep these documents true, and BG0457 records that they compare a document against a projection of itself: one computes `named = _backticked(block) & types` then asserts `types - named == set()`, which cannot fail because `named` is a subset of `types` by construction. Another is satisfied by the Revision History row describing the very change it checks. Adding prose to a document whose verifier cannot fail produces more unverified prose, and the count of things the spec claims grows while the number it guarantees stays at zero.

The repo has already solved this shape once, in `transition.py requirements`: derive the statement by RUNNING the thing, so there is no second copy to drift. A spec section listing every refusing verb and what it demands should be GENERATED from the contract reporter CR0535 proposes, not typed. Then the TRD cannot go stale, because it is not a copy.

## Impact

Every consuming project reads these documents as the contract. A sprint plan derives its test strategy from the TSD, so a TSD that does not know about a gate plans around a bar it will then hit.

## Acceptance Criteria

- [ ] A verb that gains a refusal causes a spec lane to fail until the TRD's gate inventory names it, and that inventory is GENERATED from the contract reporter rather than typed
- [ ] The TSD's test-strategy rows for a shipped gate are derived from the same source, so a sprint plan reading the TSD learns about a bar the tooling will actually apply
- [ ] The spec-agreement guards can FAIL: each of BG0457's four is shown red under the mutation its criterion names, and a guard satisfied by a Revision History row describing the change is refused - the defect that recurred independently on US0567
- [ ] The lane regenerates and diffs rather than searching for prose, so a claim cannot be satisfied by text elsewhere in the file
- [ ] The count of shipped refusing verbs NOT named in the spec is reported, so the gap is a number that can be driven to zero rather than an impression

## Recommendation

C, with B as its first slice - the generation is worthless while the comparison cannot fail, so repair the guards first and let the generated section be what they then check. Depends on CR0535: the contract reporter is the source this generates from, and building a second inventory beside it would be the same duplication one layer up.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-06 | Darren Benson | Raised |
