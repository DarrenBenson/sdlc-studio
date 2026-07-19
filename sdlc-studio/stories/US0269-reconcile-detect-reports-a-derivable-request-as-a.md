# US0269: reconcile detect reports a derivable request as a registered drift kind, using the SAME predicate the G2 gate enforces

> **Status:** Draft
> **Delivers:** CR0364
> **Created:** 2026-07-19
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py
> **Epic:** EP0087
> **Points:** 3

## User Story

**As an** operator planning against the backlog
**I want** reconcile to report a request whose children are all resolved but which is still open
**So that** the backlog stops over-reporting delivered work as remaining work

## Context

`transition._request_terminal_gate` already decides whether a request may be terminal: it returns
a block reason, or `None` to allow. The derivation must ask THAT function rather than
reimplementing "are the children resolved", or the detector and the gate can disagree about the
same request - the defect shape BG0207 and BG0211 both were.

`undecomposed_drift` is the sibling to copy: same census loop over `DISCOVERY_TYPES`, same drift
dict shape, same `two_backlog_enforced` gating in `detect_all`.

`transition` imports `reconcile` at module level, so this import must be lazy inside the function.

## Acceptance Criteria

### AC1: a derivable request is reported as a registered drift kind

- **Given** a CR that is In Progress and whose every child epic and story is terminal
- **When** `reconcile detect` runs on a project enforcing the two-backlog workflow
- **Then** it reports that CR with a drift kind present in `DRIFT_KINDS`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py -k test_a_request_with_all_children_resolved_is_reported
- **Verified:** yes (2026-07-19)

### AC2: the detector asks the G2 gate rather than reimplementing it

- **Given** the gate's definition of a resolved child changes
- **When** the detector runs
- **Then** its answer changes with it, because it calls `_request_terminal_gate` - a test fails if
  the detector carries its own child-resolution logic
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py -k test_detector_delegates_to_the_g2_gate
- **Verified:** yes (2026-07-19)

### AC3: the kind is registered, not ad hoc

- **Given** the new drift kind
- **When** `DRIFT_KINDS` is read
- **Then** the kind is in it, so every consumer that enumerates kinds sees it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py -k test_the_derivable_kind_is_registered
- **Verified:** yes (2026-07-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-19 | sdlc-studio | Groomed against the undecomposed_drift sibling and the G2 gate |
