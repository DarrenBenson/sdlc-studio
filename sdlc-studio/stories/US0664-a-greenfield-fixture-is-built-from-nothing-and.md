# US0664: A greenfield fixture is built from nothing and driven through init run to a written sprint plan, and the lane reddens when that path is broken

> **Status:** Draft
> **Delivers:** CR0542
> **Created:** 2026-08-10
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/rehearse-release.sh, .claude/skills/sdlc-studio/scripts/tests/test_rehearse_release.py
> **Epic:** EP0214
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** A greenfield fixture is built from nothing and driven through init run to a written sprint plan, and the lane reddens when that path is broken
**So that** CR0542 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1

- **Given** an empty temporary directory outside the repository
- **When** `tools/rehearse-release.sh greenfield` is run
- **Then** it builds a project with `init.py run`, writes one ordinary sized story whose declared
  paths do not exist yet, drives `sprint.py plan --write` through the shipped CLI, and exits 0
  only if a run was written - reading each command's exit status directly, never through a pipe.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_rehearse_release.py -k greenfield_reaches_a_written_plan

### AC2

- **Given** the same rehearsal
- **When** the greenfield path is broken - the fixture's grooming gate is made to refuse a unit
  whose declared paths are all creations, which is the state this repository shipped in
- **Then** the rehearsal exits non-zero and names the step that failed, proving it can fail. A
  rehearsal that is green on a tree known to be broken proves nothing.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_rehearse_release.py -k greenfield_reddens_when_the_path_is_broken

### AC3

- **Given** any run of the rehearsal
- **When** the repository's own working tree is compared before and after
- **Then** it is byte-identical: every fixture is built under a temporary root and nothing is
  written inside the repository, asserted rather than assumed.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_rehearse_release.py -k the_rehearsal_writes_nothing_into_the_working_tree

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `tools/rehearse-release.sh`, change the greenfield step to report success without invoking `sprint.py plan` | |
| AC2 | in `tools/rehearse-release.sh`, change the greenfield step's story to declare a path that already exists, so the shipped refusal is never exercised | |
| AC3 | in `tools/rehearse-release.sh`, change the fixture root from the temporary directory to the repository root | |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-10 | sdlc-studio | Created via `new` (deterministic) |
