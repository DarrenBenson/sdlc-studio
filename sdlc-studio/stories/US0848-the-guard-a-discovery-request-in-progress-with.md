# US0848: the guard: a discovery request In Progress with no unresolved child and no dated ruling is reported

> **Status:** Review
> **Delivers:** CR0591
> **Created:** 2026-09-20
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/backlog_triage.py, .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py
> **Epic:** EP0257
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** the guard: a discovery request In Progress with no unresolved child and no dated ruling is reported
**So that** CR0591 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: the check reports a discovery request that is In Progress, has no unresolved child, and carries no dated ruling

- **Given** a workspace holding three In-Progress requests: one with an unresolved child, one with every child resolved and a dated ruling row, and one with every child resolved and NO ruling
- **When** `backlog_triage.py check` runs
- **Then** only the third is reported, named by id with the reason that it is In Progress, finished by its children, and unruled - the first is working normally and the second has been judged, and reporting either would train the reader to ignore the lane
- **Mutant:** in `.claude/skills/sdlc-studio/scripts/backlog_triage.py`, report every In-Progress request whose children are all resolved, ruled or not - the lane then fires on requests that were correctly judged, becomes noise within one sweep, and gets switched off, which is the failure mode this project has already recorded for a guard whose cost is paid on every commit
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py::UnruledRequestTests::test_an_in_progress_request_with_no_unresolved_child_and_no_ruling_is_reported
- **Verified:** yes (2026-09-21)

### AC2: a request with no children at all is NOT reported by this lane

- **Given** an In-Progress request that was never decomposed and has no children
- **When** the check runs
- **Then** it is not reported here: a childless request is the separate `undecomposed` case that `status` already counts as awaiting refine, and reporting it twice under two names makes one problem look like two
- **Mutant:** in `.claude/skills/sdlc-studio/scripts/backlog_triage.py`, treat zero children as `every child resolved` - a vacuously-true reading that reports every undecomposed request as unruled and doubles the lane's output on a backlog that already has 25 of them
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py::UnruledRequestTests::test_a_childless_request_is_not_reported_as_unruled
- **Verified:** yes (2026-09-21)

### AC3: the lane is advisory and names its remedy

- **Given** a workspace with one unruled request
- **When** the check runs as the gate invokes it
- **Then** it reports rather than blocks, and its detail names the request and the action that clears it, so a reader can act without reading this story
- **Mutant:** in `.claude/skills/sdlc-studio/scripts/backlog_triage.py`, make the finding blocking - a backlog-hygiene lane that refuses a commit stops unrelated work for a state nobody created in that commit, which is the distinction between drift that predates a change and drift a change causes
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py::UnruledRequestTests::test_the_unruled_finding_is_advisory_and_names_its_remedy
- **Verified:** yes (2026-09-21)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `.claude/skills/sdlc-studio/scripts/backlog_triage.py`, report every In-Progress request whose children are all resolved, ruled or not - the lane then fires on requests that were correctly judged, becomes noise within one sweep, and gets switched off, which is the failure mode this project has already recorded for a guard whose cost is paid on every commit | the check reports a discovery request that is In Progress, has no unresolved child, and carries no dated ruling |
| AC2 | in `.claude/skills/sdlc-studio/scripts/backlog_triage.py`, treat zero children as `every child resolved` - a vacuously-true reading that reports every undecomposed request as unruled and doubles the lane's output on a backlog that already has 25 of them | a request with no children at all is NOT reported by this lane |
| AC3 | in `.claude/skills/sdlc-studio/scripts/backlog_triage.py`, make the finding blocking - a backlog-hygiene lane that refuses a commit stops unrelated work for a state nobody created in that commit, which is the distinction between drift that predates a change and drift a change causes | the lane is advisory and names its remedy |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-20 | sdlc-studio | Created via `new` (deterministic) |
