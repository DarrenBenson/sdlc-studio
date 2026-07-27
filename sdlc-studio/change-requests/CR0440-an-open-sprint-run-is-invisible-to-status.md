# CR-0440: An open sprint run is invisible to status, the one command the doctrine names for session-start re-anchoring

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/status.py, .claude/skills/sdlc-studio/help/status.md
> **Date:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (dogfooding friction, RUN-01KYHVWK resume check); agent; skill v5.0.0

## Summary

status.py contains no reference to the run state at all and offers no flag for it, so an open run is reported nowhere in the dashboard an agent is told to run first. The doctrine's standing instruction is to re-read reviews/LATEST.md and run status at session start and after any compaction, precisely to re-anchor on where the pipeline is - and the single most action-relevant fact, that a run is open with a batch mid-flight, is the one thing it omits. Only sprint preflight surfaces it, which nobody is told to run to find out whether there is a run.

## Impact

Who: any operator or agent resuming work, and every consuming project following the same doctrine. What breaks: a run opened in one session is orphaned in the next unless a human remembers its id and says so. The batch, the reviewed Sprint Goal and the token baseline all persist on disk, so the resumable state exists and is simply not reported. Compounding it, run-state.json lives under a gitignored .local/, so the run does not travel with the repo either - a teammate or a fresh clone cannot discover it at all, while the committed units it names look like ordinary unstarted backlog. Observed live on 2026-07-27: RUN-01KYHVWK held 21 units and status reported only backlog counts.

## Acceptance Criteria

- [ ] status names an open run when one exists - its id, its goal rung, the batch size and how many units remain - and says plainly that none is open when none is, so the absence is an answer rather than a silence.
- [ ] The line is derived from the run state on disk, so a run opened by any path is reported without status keeping its own copy of what a run is.
- [ ] help/status.md documents the run line, and the doctrine's session-start instruction is what a reader lands on when the reported run is one they did not open.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (dogfooding friction, RUN-01KYHVWK resume check) | Raised |
