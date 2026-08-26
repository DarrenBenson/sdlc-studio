# BG0619: a retro and a handoff can be CREATED by the shipped creator but not FOUND by id, so every id-addressed tool refuses the artefacts the close itself mints

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
> **Evidence:** `artifact.py retitle --id RETRO0109` and `--id HO0063` both refused during the RUN-01M0WCCG close on 2026-08-25. Confirmed 2026-08-26 by calling `find_by_id` over seven ids and printing `ARTIFACT_TYPES`. The creator's accepted `--type` list read from its own --help.
> **Created:** 2026-08-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`artifact.py new --type` accepts `retro`, `handoff` and `review`, and `sprint close` mints both a retro and a handoff on every run. But `sdlc_md.ARTIFACT_TYPES` holds only bug, charter, cr, epic, issue, plan, rfc, story, test-spec and workflow, and `find_by_id` iterates exactly that map. Measured 2026-08-26: `find_by_id` resolves BG0615, US0676, EP0217, CR0558 and TS0001, and returns None for RETRO0109 and HO0063 - artefacts that exist, are indexed, and were written by the shipped creator minutes earlier. Twelve scripts read `find_by_id`, so the refusal is not local to one verb: `artifact.py retitle --id RETRO0109` answers `no artifact found for id 'RETRO0109'`, and the same is true for the handoff. The creator and the resolver disagree about which types exist.

## Steps to Reproduce

1. `sprint.py close --retro RETROxxxx`, which mints a retro and a handoff. 2. Try to correct either one's title with the deterministic writer: `artifact.py retitle --id RETRO0109 --title '<new>'`. 3. It answers `no artifact found`. Measured on RETRO0109 and HO0063, 2026-08-25, where both had to be renamed by hand across the file, the H1 and the index row, plus an inbound link repaired in the retro body.

## Proposed Fix

Make the resolver's type map agree with the creator's. Either add retro, handoff and review to `ARTIFACT_TYPES` with their directories and id prefixes, or - if a retro is deliberately not a first-class addressable artefact - have `artifact.py new` refuse to mint one and say why, so the two surfaces state one rule between them. A test that asserts every `--type` choice the creator offers is resolvable by `find_by_id` would pin whichever answer is chosen, and is the piece missing today.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `artifact.py new --type` accepts `retro`, `handoff` and `review`, and `sprint close` mints both a retro and a handoff on every run.
- [ ] **AC2** The proposed fix lands, pinned by a test: Make the resolver's type map agree with the creator's.

## Impact

The doctrine's rule is that mechanical work goes through a tool and hand-authoring is an error. `retitle` exists because a title lives in three places at once and a hand correction means editing all three plus every inbound link - which is exactly what had to be done twice at the last close, on the two artefacts the close had just written. A gap in the resolver quietly converts the tool-first rule into hand-editing for the artefact class that records what a run did.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-26 | sdlc-studio | Filed |
