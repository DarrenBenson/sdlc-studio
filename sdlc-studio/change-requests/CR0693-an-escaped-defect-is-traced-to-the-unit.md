# CR-0693: An escaped defect is traced to the unit and verdict that let it through, and its cause reaches the next plan, build and review

> **Status:** Proposed
> **Parent:** RFC0063
> **Depends on:** RFC0064 (D2); EP0280
> **Related:** RFC0064
> **Priority:** High
> **Type:** feature
> **Size:** L
> **Date:** 2026-11-10
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson (operator); human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-10T12:22:12Z

## Summary

RFC0063 WS6 and O12: a defect that escapes to production is traced to the unit and the verdict that let it through, and the next plan, build and review carry what it taught. Today the bug template has a free-text Root Cause Analysis section, but no field marks a bug as a production escape or ties it to a unit, a verdict or a release.

Filed with its dependency on RFC0064 recorded (D0456). D1 is decided: an incident is an issue with a root-cause section (D0457). How a root cause reaches agents still waits for RFC0064's D2. RFC0063 also sequences this after EP0280.

## Impact

Serves O12, Abena Osei's End goal 4 and Graham Doyle's End goal 3. Feeds the WS6 scorecard (escapes per 100 points) and RFC0064's change failure rate.

## Acceptance Criteria

- [ ] A bug found in production records that it escaped, the release it shipped in, and the unit and review verdict that let it through; a command proposes the unit from the release and the files the fix touches
- [ ] An incident is recorded as an issue with a root-cause section and triaged into the escaped bugs it caused, each linked back to it (D0457)
- [ ] The sprint report and the scorecard state escapes per 100 points delivered, from the linked records
- [ ] Pending RFC0064 D2: an escape's root cause reaches the next plan, build and review as D2 decides, within RFC0062's context budget

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-10 | Darren Benson (operator) | Raised |
