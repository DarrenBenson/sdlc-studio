# BG0441: review_coverage launders a recorded REJECT into coverage through the evidence lane, so the gate certifying a close reports a rejected unit as reviewed

> **Status:** Fixed
> **Severity:** Critical
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py
> **Evidence:** Severity is Critical because of what consumed this gate. The ten Done stories of the 2026-07-30 batch were held at Review and released only under explicit conformance waivers D0077-D0086, recorded on the reasoning that no APPROVE had been earned. This gate reports those same ten as covered. Had the close been driven by `review_coverage` rather than by `conformance`, all ten would have passed as independently reviewed with no waiver, no operator ruling, and nothing in the record showing a REJECT had been overridden. The waivers are what stopped it, and they were recorded by hand.
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** engineering amigo seat (independent, isolated worktree), reproduced by author; human; v1
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

`sprint.review_coverage` tries three lanes per unit: the per-unit verdict, the adversarial evidence row, then the batch review. The first and third are verdicted; the middle one is not, by deliberate design (an evidence row carries no verdict column, so recording the pass IS the claim). The lanes are tried in sequence with a `continue` between them. A unit whose per-unit verdict is a REJECT therefore FAILS lane one and falls straight through to lane two, where only independence is tested and no verdict is consulted, and is returned covered. The REJECT is not overridden by a better verdict; it is overridden by a lane that cannot see verdicts at all. `conformance.py:319-320` gets the identical rule right, with a comment saying a recorded per-unit REJECT is not papered over - so the batch's newer gate is strictly weaker than the one beside it, and the two disagree about the same units.

## Steps to Reproduce

Executed on this repository at d7a1ad8f, 2026-07-30.

```text
python3 -c "
import sys; sys.path.insert(0,'.claude/skills/sdlc-studio/scripts')
import sprint, critic
for u in ['US0485','US0484','US0461']:
    print(u, `sprint.review_coverage(`'.',[u])[u], (`critic.verdict_for(`'.',u) or {}).get('verdict'))
"
```

Actual output:

```text
US0485 {'covered': True, 'by': 'adversarial evidence'} REJECT
US0484 {'covered': True, 'by': 'adversarial evidence'} REJECT
US0461 {'covered': True, 'by': 'adversarial evidence'} REJECT
```

Every one of those verdicts is a REJECT whose own issues text reads "No re-review of the repairs has been run, so no APPROVE is earned. This REJECT stands as the adversarial verdict of record." The gate reads all three as covered.

The two tests that claim this ground cannot fail on the shape the repository actually produces: `test_sprint.py::test_a_recorded_REJECT_does_not_cover_a_unit` and `::test_a_per_unit_REJECT_is_not_covered_either` each build a repo with a verdict row and NO evidence row, so neither ever reaches lane two. A REJECT plus an evidence row - the shape every reviewed-and-rejected unit in this corpus has - is untested.

Found by the engineering amigo seat during the close of RUN-01KYPZ1G, then reproduced independently by the author before filing.

## Proposed Fix

The lane sequence is the defect, not the evidence lane's verdict-blindness. An evidence row legitimately carries no verdict, but it must not be reachable as a SUBSTITUTE for a verdict that exists and is negative.

1. Consult the per-unit verdict FIRST and let a recorded REJECT be terminal for the unit: if a verdict exists and is not an APPROVE, the unit is not covered, and no later lane may reconsider it. Falling through to a weaker lane on a negative verdict is the bug; falling through on the ABSENCE of a verdict is the intended behaviour and must be preserved.
2. Both guarding tests are rebuilt around the real shape - a REJECT WITH an evidence row present - since a test that cannot reach the defective branch is the reason this shipped.
3. `conformance.py` and `sprint.py` must not carry two independent implementations of one rule. Whichever way this is fixed, one of them should call the other, or a test should assert the two agree over a matrix of verdict and evidence combinations. They currently disagree, and the disagreement is silent.

Also worth settling during refine: whether the coverage figure should distinguish a REJECT from an absent review at all, which is CR0506's subject. This bug is the narrower and more urgent half - CR0506 asks for a third state, whereas this is the existing two states being computed wrongly.

> **Verification depth:** functional - the fix is exercised through `sprint.review_coverage` over a repo carrying a REJECT and an evidence row, with two controls and an unreadable-ledger control; all three mutants (guard removed, guard over-broad, unreadable ledger read as rejection) KILLED with unique anchors asserted, `__pycache__` purged and `python3 -B`.

## Acceptance Criteria

### AC1: a recorded REJECT is terminal, on the shape the corpus actually holds

- **Given** a unit carrying a REJECT verdict AND an adversarial evidence row - the shape every reviewed-and-rejected unit in this workspace has, and the one the two pre-existing tests could not reach because both build a repo with no evidence row
- **When** review_coverage runs
- **Then** the unit is NOT covered: the REJECT is terminal and no later lane reconsiders it, where before it fell through into a lane that carries no verdict column by design and so could not see it had been rejected
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::BatchBoundaryReviewTests::test_a_REJECT_is_not_laundered_into_coverage_by_the_evidence_lane
- **Verified:** yes (2026-07-30)

### AC2: the evidence lane still covers a unit that was never rejected

- **Given** a unit with an independent evidence row and no verdict at all
- **When** review_coverage runs
- **Then** it is still covered by that lane - the control, without which this fix is indistinguishable from deleting the evidence lane; absence of a verdict must fall through, only a verdict that exists and is not an APPROVE stops the search
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::BatchBoundaryReviewTests::test_an_evidence_row_still_covers_a_unit_that_was_never_rejected
- **Verified:** yes (2026-07-30)

### AC3: an unreadable verdict ledger does not manufacture a rejection

- **Given** a unit whose verdict ledger cannot be read, reached through review_coverage rather than the helper because a library test is not a lane test
- **When** review_coverage runs
- **Then** the unit is judged by its lanes rather than treated as rejected - added because this mutant SURVIVED the first three, and answering 'rejected' on a filesystem error invents a verdict nobody gave
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::BatchBoundaryReviewTests::test_an_unreadable_verdict_ledger_does_not_manufacture_a_rejection
- **Verified:** yes (2026-07-30)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | engineering amigo seat (independent, isolated worktree), reproduced by author | Filed |
