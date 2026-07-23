# US0322: The claim pass runs BEFORE the logic review and reports separately, so a prose-only round is visibly a different kind of round

> **Status:** Done
> **Depends on:** US0320
> **Delivers:** CR0393
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/review_prep.py
> **Epic:** EP0109
> **Points:** 3

## User Story

**As an** operator deciding whether to buy another review round
**I want** a round that found only prose defects to look different from one that found logic
defects
**So that** I can tell convergence from churn, which is the judgement rounds 8, 9 and 10 of
RUN-01KY3MFX needed and could not make

## Acceptance Criteria

### AC1: the claim pass is ordered before the logic review

- **Given** the review inputs emitted for a round
- **When** the phases are read
- **Then** the claim pass precedes the logic review, and a round recording logic findings
  with no claim pass run is reported incomplete rather than accepted
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_review_prep.py::ClaimPassOrderTests::test_a_round_with_logic_findings_and_no_claim_pass_is_incomplete
- **Verified:** yes (2026-07-23)

### AC2: the two kinds of finding are reported separately

- **Given** a round with two prose findings and no logic findings
- **When** its outcome is rendered
- **Then** the counts are reported apart, so a prose-only round is visibly a different kind
  of round, and a reader can see the code converged while the prose did not
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_review_prep.py::ClaimPassOrderTests::test_prose_and_logic_findings_are_counted_separately
- **Verified:** yes (2026-07-23)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
