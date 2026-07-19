# US0246: close the accepted-tranche decision rows with what actually shipped

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/rfcs/RFC0035-the-sprint-report-what-a-sprint-delivered-what.md, sdlc-studio/rfcs/RFC0037-backlog-triage-as-a-first-class-ceremony-keep.md, sdlc-studio/rfcs/RFC0038-close-the-estimator-loop.md, sdlc-studio/rfcs/RFC0039-the-discovery-track-issue-refine-and-triage-a.md, sdlc-studio/rfcs/RFC0042-make-the-sprint-close-down-un-skippable-enforce.md
> **Epic:** EP0079
> **Points:** 2

## User Story

**As a** reader of an accepted RFC
**I want** its decision rows to record what was actually decided and shipped
**So that** the design record matches the delivered code instead of an unanswered question

## Acceptance Criteria

### AC1: Close the tranche rows with the decision that shipped

- **Given** the 2026-07-14 tranche accepted while carrying an unanswered decision row, RFC0035 and RFC0038 among them
- **When** each row is closed against the code that shipped from it
- **Then** the row reads Closed and states the option taken, naming the delivering CR or epic, and a revision-history row records the closure and its date
- **Verify:** grep "D1 .* Closed" sdlc-studio/rfcs/RFC0035-the-sprint-report-what-a-sprint-delivered-what.md

### AC2: No Accepted RFC is left with an Open decision

- **Given** the RFC workspace after the tranche is closed
- **When** every RFC in Accepted state is scanned
- **Then** none carries a decision row still marked Open, so the newly enforced gate holds over existing files and not only over future transitions
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_rfc.py -k AcceptedTrancheDecisionsClosedTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
