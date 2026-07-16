# CR-0264: The filer has no duplicate detection: three overlapping pairs accumulated in one backlog of eleven

> **Status:** Superseded
> **Size:** M
> **Priority:** P2
> **Type:** Feature
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/sprint.py
> **Date:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Nothing checks whether a new finding overlaps an artefact that is already open. In a single day of dogfooding, an agent filing findings at speed produced THREE duplicate pairs in a backlog of eleven, and every one was caught by accident rather than by tooling.

BG0139 (the model router scores a docs unit trivial) turned out to be entirely SUBSUMED by CR0262 (the forecast seed is inert): BG0139 fix (a) is CR0262 AC4 verbatim, and BG0139 (b) and (c) are CR0262 AC1 and AC2. The same change, filed twice, hours apart, by the same agent.

CR0261 (record which model delivered a unit) and CR0263 (measure the estimator, per estimator) are structurally identical: both add an attribution field to telemetry and segment the accuracy report by it, in the same two files.

BG0137 and BG0138 are both link defects fixed in `check_links.py.`

They were noticed only because CR0260 shared-file clustering put them in the same collision cluster and forced a second look. Without that they would have been scheduled as independent work, and two agents would have been dispatched to write the same fix into the same file concurrently - which is precisely the collision the cluster detection exists to prevent, arriving through the front door instead.

The cost is not just wasted work. A duplicate inflates the backlog, double-counts in every status report, and splits the acceptance criteria for one change across two artefacts, so neither is complete on its own.

## Impact

Every filing, and it gets worse the faster findings are raised - which is exactly what this project encourages. An agent under instruction to raise every friction it hits will generate near-duplicates by construction, and the tool currently rewards volume over coherence.

**Effort:** M

## Acceptance Criteria

- [ ] At filing, a finding whose Affects files and subject substantially overlap an OPEN artefact is surfaced to the author with the candidate named, before the id is minted. It warns and shows the overlap; it does not silently refuse, because a genuine near-miss is common and the author is the one who can tell them apart.
- [ ] The overlap check is mechanical and stated: what it compares (Affects intersection, title and summary similarity) and what it deliberately lets through, so an author can trust it rather than route around it.
- [ ] sprint plan surfaces suspected duplicates in a batch alongside the shared-file clusters, since two units in one cluster with near-identical acceptance criteria are more likely one unit than two.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Raised |
