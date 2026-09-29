# CR-0604: The andon cord stops the run on an irreversible action or an operating-domain exit

> **Status:** Proposed
> **Parent:** RFC0060
> **Priority:** Medium
> **Type:** Feature
> **Size:** M
> **Date:** 2026-09-29
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-29T09:34:19Z

## Summary

RFC0060 workstream 4 (D0233): a named, short list of conditions halts the line and wakes the operator - exactly two: an irreversible action (push, tag, release, delete) and an exit from the run's operational design domain (US0866). Everything else the line handles by itself. The RFC names this work 'CR (TBD)'; this is that change request, so the site's 'next in 6.x' label for the andon cord tracks an artefact that can ship.

## Impact

Without it a v6 run has no mechanical stop rule: the operator is woken by whatever each step happens to refuse, and an irreversible action is guarded only by the hooks and the operator's approval.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-29 | sdlc-studio | Raised |
