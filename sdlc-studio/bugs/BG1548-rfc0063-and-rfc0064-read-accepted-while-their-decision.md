# BG1548: RFC0063 and RFC0064 read Accepted while their Decision sections still say pending and four workstreams have no CR

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** sdlc-studio/rfcs/RFC0063-human-in-the-lead-the-accountable-engineering-lead.md, sdlc-studio/rfcs/RFC0064-production-learning-and-risk-proportionate-review.md, tools/lint_corpus.py, tools/tests/test_lint_corpus.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, rfc lens, survived 3 of 3 refute votes; observed at sdlc-studio/rfcs/RFC0063-human-in-the-lead-the-accountable-engineering-lead.md ## Decision (lines 158-166) and ## Phased Plan / Workstreams rows WS2, WS5, WS6, WS7; rfcs/RFC0064-*.md ## Decision (lines 148-154)
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:28:01Z

## Summary

RFC0063 and RFC0064 were moved to Accepted on 2026-11-14 under D0474, but the Decision section the RFC template says is filled on acceptance was never filled in either. RFC0063 lines 162 to 164 still give the outcome as pending `rfc decide` with decisions D2, D3, D4, D8, D9 and D10 open, although its own Open Decisions table marks all six Resolved; RFC0064 lines 152 to 154 read pending in the same three fields. RFC0060 and RFC0061 show the filled form, so this is a slip in the record, not house style. Behind the stale text sits a tracking gap: RFC0063's workstream table promises a new CR for WS2 (the role model and owner field), the monthly team budget view in WS5, the model scorecard in WS6 and the machinery guardrail in WS7, and none is in its Decomposed-into line or anywhere in the backlog. The RFC schedules that work for 2027 Q1, but D0388 says an accepted RFC's delivery is tracked by the units it decomposes into, so these four are tracked by nothing, and CR0698 already depends on the scorecard that has no unit.

## Steps to Reproduce

1. Open sdlc-studio/rfcs/RFC0063-human-in-the-lead-the-accountable-engineering-lead.md. Line 3 reads Status Accepted.
2. Read its Decision section at lines 162 to 164. Observed: the Outcome, Rationale and Spawned CRs lines all read pending, and the Outcome says six decisions remain open.
3. Read its Open Decisions table. Observed: the same six decisions are marked Resolved.
4. Read the Decision section of RFC0064 at lines 152 to 154. Observed: the same three pending lines under Status Accepted.
5. Compare RFC0063's workstream rows WS2, WS5, WS6 and WS7, each promising a new CR, with its Decomposed-into line (CR0689 to CR0694, CR0702, CR0704, CR0706) and search the change requests for the owner field, the monthly budget view, the model scorecard and the maintenance declaration. Observed: no unit carries any of them.
6. Expected: an Accepted RFC states its outcome, rationale and spawned units, and every workstream row marked as a new CR names a unit or a recorded deferral.

## Proposed Fix

Fill the Decision section of both RFCs with the outcome, the date, the rationale and the decisions that resolved each open question (D0436 to D0441 and D0457 to D0462, per D0474), and list the spawned CRs. For RFC0063's WS2, the WS5 budget view, the WS6 scorecard and WS7, either file a CR for each and add it to Decomposed-into, or record against each row the decision that defers it to 2027 Q1 so the deferral is written in the RFC and not only in a sequencing sentence. Add a revision history row to each RFC. To stop it recurring, add a check to tools/`lint_corpus.py` that reports an Accepted RFC whose Decision outcome still reads pending, with a test.

## Acceptance Criteria

- [ ] **AC1** Given a fixture corpus holding an Accepted RFC whose Decision Outcome still reads pending, when `tools/lint_corpus.py` runs, then it reports a finding naming that RFC; a Proposed RFC with a pending Outcome and an Accepted RFC with a filled Decision beside it are not reported. Fails on: an Accepted RFC with an unfilled Decision reading as clean, or a finding against an RFC not yet decided.
  - **Verify:** pytest tools/tests/test_lint_corpus.py::AcceptedRfcDecisionTests::test_an_accepted_rfc_with_a_pending_outcome_is_reported
- [ ] **AC2** Given this repository's RFCs after the fix, when the new rule reads them, then it reports nothing: the Decision sections of RFC0063 and RFC0064 state the outcome, the date, the rationale, the decisions that resolved each open question and the spawned CRs. Fails on: either RFC still reading pending under Status Accepted.
  - **Verify:** pytest tools/tests/test_lint_corpus.py::CorpusLaneRunsOnThisRepo::test_no_accepted_rfc_here_has_a_pending_decision
- [ ] **AC3** Given RFC0063's workstream table after the fix, when rows WS2, WS5 (the monthly budget view), WS6 (the model scorecard) and WS7 are read, then each names a CR that is also in the Decomposed-into line, or the decision that defers it, and each RFC carries a Revision History row for the correction. Fails on: a workstream row promising a new CR that no unit or recorded deferral carries.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
