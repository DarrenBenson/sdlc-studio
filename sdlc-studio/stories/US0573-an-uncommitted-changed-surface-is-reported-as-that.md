# US0573: an uncommitted changed surface is reported as that REASON, naming the isolated-checkout and register routes to measured evidence

> **Status:** Review
> **Delivers:** CR0502
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, sdlc-studio/stories/US0573-an-uncommitted-changed-surface-is-reported-as-that.md
> **Epic:** EP0193
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** an author reading the mutation lane's verdict on their own change
**I want** an uncommitted surface reported as that reason, with both routes to measured evidence named
**So that** the lane tells me what to do instead of reporting the same thing whatever I did

## Acceptance Criteria

### AC1: an uncommitted surface is reported as THAT reason, not as no evidence

- **Given** a changed surface with uncommitted work on it, which the runner correctly refuses to mutate
- **When** the mutation lane reports
- **Then** it names the uncommitted state as the reason, distinct from a surface nobody tested - only one of those is the author's omission, and an advisory that says the same thing either way gets read as scenery
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::UncommittedSurfaceCLITests::test_an_uncommitted_surface_is_reported_as_that_reason
- **Verified:** yes (2026-08-07)

### AC2: the reason names BOTH routes to measured evidence

- **Given** the uncommitted-surface reason
- **When** it is printed
- **Then** it names the isolated checkout and `register` for a hand-applied mutant, with the discipline that makes a hand run trustworthy - a unique anchor asserted, bytecode purged, the patch proven to have changed the file
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::UncommittedSurfaceCLITests::test_the_reason_names_both_routes_to_measured_evidence
- **Verified:** yes (2026-08-07)

### AC3: a COMMITTED surface with no evidence still reports no evidence

- **Given** a committed changed surface that has never been mutated
- **When** the mutation lane reports
- **Then** it still reports no evidence - the control, without which this change could be an excuse that silences the lane rather than a distinction that sharpens it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::UncommittedSurfaceCLITests::test_a_committed_untested_surface_still_reports_no_evidence
- **Verified:** yes (2026-08-07)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-07 | sdlc-studio | Every `Verified: yes` stamp retracted and every verifier re-pointed at a test that drives the shipped command. The stamps were false: each criterion names `transition.py set` or the mutation lane as its When while its verifier called the library function, which is why BG0541's missing wiring passed this wave. Raised by the plan-time qa and engineering seats |
| 2026-08-07 | sdlc-studio | Re-verified through `mutation.py run`, which found the criterion FALSE at the shipped entry point: the refusal a person actually reads named only the worktree route, while `series_reason` - the string the library test asserted on - named both. The refusal now names both, with the discipline that makes a hand run trustworthy |
