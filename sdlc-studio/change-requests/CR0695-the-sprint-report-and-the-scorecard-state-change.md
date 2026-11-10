# CR-0695: The sprint report and the scorecard state change failure rate, from releases and the incidents linked to them

> **Status:** Proposed
> **Parent:** RFC0064
> **Depends on:** CR0693
> **Priority:** High
> **Type:** feature
> **Size:** M
> **Date:** 2026-11-10
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson (operator); human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-10T13:39:08Z

## Summary

RFC0064 WS2. A release is the deploy (D0458): change failure rate is the releases with at least one linked incident divided by the releases counted. Incidents are issues with a root-cause section (D0457), linked to the release their escaped bugs shipped in (CR0693). The figure sits beside escapes per 100 points.

## Impact

Serves O12 and Graham Doyle's End goal 3 (fewer surprises in production). Adds no step: it is derived from records the release cut and incident triage already write.

## Acceptance Criteria

- [ ] A command derives change failure rate from the committed release records and the incident issues linked to them, naming the releases counted and the window
- [ ] The sprint report and the scorecard show change failure rate beside escapes per 100 points, each naming its source records
- [ ] A release younger than a stated settling period is shown as pending, not counted as a success
- [ ] With no incident record or no release in the window, the row reads 'not measured: <reason>', never 0%

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-10 | Darren Benson (operator) | Raised |
