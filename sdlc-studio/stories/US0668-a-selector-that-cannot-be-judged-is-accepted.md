# US0668: A selector that cannot be JUDGED is accepted and reported unjudged, never refused, so a missing runner never makes the writer unusable

> **Status:** Done
> **Delivers:** CR0508
> **Created:** 2026-08-11
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Epic:** EP0215
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** A selector that cannot be JUDGED is accepted and reported unjudged, never refused, so a missing runner never makes the writer unusable
**So that** CR0508 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1

- **Given** a `Verify:` line the resolver cannot JUDGE - an unknown runner, a `shell` verifier, or
  a runner not installed on this machine
- **When** the artefact is written
- **Then** it is ACCEPTED and reported as unjudged. Refusing what cannot be judged would make
  every writer unusable on a machine missing one runner, which is a worse failure than the one
  being fixed.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py -k an_unjudgeable_selector_is_accepted_and_reported
- **Verified:** yes (2026-08-11)
- **Mutant:** in `file_finding.py`, treat an unjudgeable selector as unresolvable and refuse it.

### AC2

- **Given** the same writer
- **When** a selector that CAN be judged and does not resolve is written
- **Then** it is still refused - the positive control, without which "accept what cannot be
  judged" is satisfied by accepting everything.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py -k a_judgeable_unresolvable_selector_is_still_refused
- **Verified:** yes (2026-08-11)
- **Mutant:** in `file_finding.py`, classify every selector as unjudgeable.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `file_finding.py`, change an unjudgeable selector to be treated as unresolvable and refused | |
| AC2 | in `file_finding.py`, change every selector to be classified unjudgeable | |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-11 | sdlc-studio | Created via `new` (deterministic) |
