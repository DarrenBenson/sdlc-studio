# BG1561: Three 6.4 epics read Done while their own completion-bar criteria are undelivered, unticked and point nowhere

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** sdlc-studio/epics/EP0308-a-change-board-can-approve-a-release-from.md, sdlc-studio/epics/EP0309-an-escaped-defect-is-traced-to-the-unit.md, sdlc-studio/epics/EP0311-builder-and-reviewer-reasoning-effort-is-a-project.md, tools/tests/test_epic_completion_bar_carried.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, stories lens, survived 2 of 3 refute votes; observed at sdlc-studio/epics/EP0309-an-escaped-defect-is-traced-to-the-unit.md 'Acceptance Criteria (Epic Level)' sections of EP0309, EP0308 and EP0311
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:29:32Z

## Summary

EP0308, EP0309 and EP0311 each copy their parent request's criteria under a line saying these are the epic's completion bar, not any single story's, and each has a status of Done derived from its stories alone. In EP0309 the incident record, escapes per 100 points and plan-time file matching were never built and are carried by CR0706; in EP0308 grouping by risk class and the annex read are carried by CR0704; in EP0311 the low-against-medium trial is carried by CR0710. All four boxes in each epic are unticked, the revision history holds only the creation row, and none of the three files names the request that now carries the remainder. A reader of the epic cannot tell a delivered bar from a deferred one. BG1452, which is open, records the same derivation for the parent request and proposes a fix for requests only, so its fix as written would leave these epics reading Done.

## Steps to Reproduce

1. Open sdlc-studio/epics/EP0309-an-escaped-defect-is-traced-to-the-unit.md: the Status is Done, the Acceptance Criteria (Epic Level) section says the criteria are the epic's completion bar, and all four boxes are unticked.
2. Search the skill's scripts and pages for per 100 points and for escapes per: nothing matches. Search scripts/escape.py for incident: nothing matches.
3. Open the EP0308 and EP0311 files under sdlc-studio/epics/: both are Done with four unticked epic-level boxes and a revision history holding only the creation row.
4. Count the mentions of CR0704, CR0706 and CR0710 in the three epic files: zero in each.
5. Open CR0704, CR0706 and CR0710 under sdlc-studio/change-requests/ and confirm each carries the undelivered part of one of the three epics.

## Proposed Fix

In each of the three epics, tick the epic-level criteria that were delivered, mark each undelivered criterion as carried and name the request that carries it (CR0704 for EP0308, CR0706 for EP0309, CR0710 for EP0311), and add a revision row recording the deferral. Add a repository test that fails when an epic at Done has an unticked epic-level criterion with no carrying id beside it, with a positive control for an epic whose boxes are all ticked. The tooling half, deriving Done only when the completion bar is met or explicitly carried, belongs with BG1452, whose scope should be widened to the epic's copied bar.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: EP0308, EP0309 and EP0311 each copy their parent request's criteria under a line saying these are the epic's completion bar, not any single story's, and each...
- [ ] **AC2** The proposed fix lands, pinned by a test: In each of the three epics, tick the epic-level criteria that were delivered, mark each undelivered criterion as carried and name the request that carries it...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
