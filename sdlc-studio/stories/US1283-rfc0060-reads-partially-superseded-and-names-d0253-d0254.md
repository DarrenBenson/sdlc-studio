# US1283: RFC0060 reads partially superseded and names D0253, D0254 and D0290, and D0236 is superseded in the log

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0723
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/rfcs/RFC0060-the-dark-factory-a-sprint-that-decides-for.md, sdlc-studio/decisions.md
> **Epic:** EP0361
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** RFC0060 reads partially superseded and names D0253, D0254 and D0290, and D0236 is superseded in the log
**So that** CR0723 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: RFC0060 reads Accepted (partially superseded)

- **Given** RFC0060 and the RFC index
- **When** the RFC's status is changed with the shipped tool and the index is read
- **Then** the status line reads Accepted (partially superseded), the form RFC0009 uses, and the RFC index row agrees. Fails on: a status that still reads plain Accepted, or an index row edited by hand that the next reconcile would rewrite
- **Verify:** manual read the records the criterion names and confirm each reads as stated; paperwork only, no test can pin it

### AC2: The RFC names the decisions that overturned it and the rulings that stand

- **Given** RFC0060's Decision section, Open Decisions table and workstream rows
- **When** they are read against D0253, D0254 and D0290 in `sdlc-studio/decisions.md`
- **Then** they name D0253 and D0254 as superseding D0230 and D0231, name D0290 as declining the derived domain record and the stop-detection machinery, state that D0232, D0233 and D0235 stand, and no row reads 'CR to be decided'. Fails on: a workstream row that still presents a cancelled workstream as pending, or a ruling quoted that the decisions log shows superseded
- **Verify:** manual read the records the criterion names and confirm each reads as stated; paperwork only, no test can pin it

### AC3: Each Decomposed-into entry shows how it closed

- **Given** RFC0060's Decomposed-into line and its revision history
- **When** they are read against the four artefacts
- **Then** EP0258, EP0259 and CR0593 are each shown as Superseded and CR0604 as Rejected, matching each artefact's own status, and a revision history row dated the day of the change records it. Fails on: an entry with no closing status, or one that differs from the artefact's status line
- **Verify:** manual read the records the criterion names and confirm each reads as stated; paperwork only, no test can pin it

### AC4: D0236 no longer reads as an accepted plan

- **Given** D0236 in `sdlc-studio/decisions.md`
- **When** the log is read
- **Then** D0236 is marked superseded, or a newer accepted row names D0236 in its supersedes cell and says the run plan was cancelled by D0253, D0254 and D0290. Fails on: a log that still shows the cancelled run plan as accepted with nothing superseding it
- **Verify:** manual read the records the criterion names and confirm each reads as stated; paperwork only, no test can pin it

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
