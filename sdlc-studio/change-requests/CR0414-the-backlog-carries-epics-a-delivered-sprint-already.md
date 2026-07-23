# CR-0414: the backlog carries epics a delivered sprint already satisfied and nothing detects it: EP0125's shared prose-helper stories were largely built as EP0146, but built-not-closed reads the verify-report so an ungroomed skeleton with no verifiers is invisible to it

> **Status:** Proposed
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/scripts/audit.py
> **Priority:** Medium
> **Type:** Feature
> **Size:** M

## Summary

{{what changes and why}}

## Impact

{{who this affects and what breaks}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |

## Detail

Found while composing Sprint 2. EP0125 ("Prose reaches every creation script without a shell",
stories US0361-US0364) sits Draft on the delivery backlog. Sprint 1 then delivered EP0146, whose
`file_finding.resolve_prose_fields` IS the shared fields-file helper US0361 asks for, adopted
across the prose writers US0361 names; and whose `shell_hazards` IS the command-substitution
fingerprint detector US0362 asks for. Neither epic references the other. Two refines, months
apart, minted the same goal twice, and a whole sprint delivered one of them without anything
noticing the other was now largely satisfied.

**Why the existing detector misses it.** EP0130's `built-not-closed` flag is deliberately
mechanical: it reads `.local/verify-report.json` and fires only where a unit's executable ACs all
pass. An ungroomed skeleton has no `Verify:` lines, so it can never appear in that report, so the
one check built for "this is already done" is structurally blind to the case that matters most -
work minted before it was groomed. The audit's `already-satisfied` lens has the same basis and the
same blindness.

The gap is SEMANTIC overlap between a planned unit and delivered work, which no mechanical
signal in the workspace currently covers. This is the two-backlog model's blind spot: refine
mints against the request, never against what has since shipped.

## Impact

Every long-lived backlog. Here it would have wasted a 12-point epic in Sprint 2 had the overlap
not been spotted by eye. The failure mode is silent and grows with backlog age: the older the
skeleton, the likelier some later sprint satisfied it.

## Acceptance Criteria

- [ ] AC1: plan-time overlap detection that does not depend on verifiers
- **Given** a batch holding a unit whose title/summary closely matches work already delivered (a terminal unit, or a shipped epic touching the same Affects)
- **When** `sprint plan` runs
- **Then** it reports the candidate overlap with the delivered id, so the operator triages before the batch is built - advisory, never a refusal
- **Verify:** manual

- [ ] AC2: the report distinguishes overlap from mere file-sharing
- **Given** two units that touch the same file but do different work
- **Then** they are NOT reported as overlapping - a shared `Affects` alone is the existing cluster signal and must not be recycled as a duplicate claim
- **Verify:** manual

- [ ] AC3: the blind spot is documented where the existing detector is
- **Given** a reader of the built-not-closed behaviour
- **Then** the docs state plainly that it reads the verify-report and therefore cannot see an ungroomed unit, naming this check as the complement
- **Verify:** manual
