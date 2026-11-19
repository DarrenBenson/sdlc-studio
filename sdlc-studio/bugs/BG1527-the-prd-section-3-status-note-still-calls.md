# BG1527: The PRD section 3 status note still calls the shipped token forecast a falsified hypothesis

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** sdlc-studio/prd.md, tools/tests/test_lean_prd_refresh.py, changelog.d/BG1527.md
> **Evidence:** audit AUDIT-2026-11-17, project profile, prd lens, survived 3 of 3 refute votes; observed at sdlc-studio/prd.md Section 3 'Complete vs Ready' note, lines 230-232, against the Sizing and velocity loop row (line 284) and Section 10 (lines 722-736, 752-757)
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:22:43Z

## Summary

The note in section 3 of the PRD that explains how to read every Status cell says that Complete is not the same as calibrated, and that the token forecast under Sizing and velocity ships and runs while its prediction is a falsified hypothesis. The row it points at says points are the first cost predictor to clear the pre-registered bar, and section 10 says the falsified predictor was replaced and that the sizing feature now earns a cost claim. The matching open question is marked closed. The note is residue from before the predictor was replaced, left behind when the row and section 10 were rewritten. It tells the reader the shipped forecast is known to be wrong, which is the opposite of the cost claim that outcome O11 and the Cost forecast row rest on.

## Steps to Reproduce

1. Read sdlc-studio/prd.md lines 230 to 232: the note says the token forecast's prediction is a falsified hypothesis and points to section 10.
2. Read the Sizing and velocity loop row at about line 284: points are the first cost predictor to clear the pre-registered bar.
3. Read section 10 at about lines 722 to 736 and 752 to 757: the falsified predictor was replaced, and the sizing feature earns a cost claim.
4. Read the Open Questions entry at about line 766: the predictor question is closed.

## Proposed Fix

Rewrite the note so it keeps the distinction between Complete and calibrated but describes the present state: the earlier token predictor was falsified and replaced, and the points-based forecast cleared the pre-registered bar, with the section 10 reference kept. Add a check to the PRD refresh test that fails when the phrase falsified hypothesis describes the shipped forecast.

## Acceptance Criteria

- [ ] **AC1** Given the Complete versus calibrated note in section 3 of `sdlc-studio/prd.md`, when it is read, then it keeps that distinction and describes the present state: the earlier token predictor was falsified and replaced, the points-based forecast cleared the pre-registered bar, and the section 10 reference stays. Fails on: the phrase falsified hypothesis describing the shipped forecast.
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py::PrdRefreshTests::test_the_status_note_does_not_call_the_shipped_forecast_falsified

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
