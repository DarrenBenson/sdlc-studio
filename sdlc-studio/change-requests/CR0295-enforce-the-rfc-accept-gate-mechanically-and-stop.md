# CR-0295: Enforce the RFC accept gate mechanically and stop file_finding.py manufacturing the content-free 'Act on this finding or keep status quo' Open row - the whole 2026-07-14 tranche is Accepted with boilerplate Open decisions

> **Status:** In Progress
> **Decomposed-into:** EP0079
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/reference-rfc.md, sdlc-studio/rfcs/RFC0035-*.md, sdlc-studio/rfcs/RFC0037-*.md, sdlc-studio/rfcs/RFC0038-*.md, sdlc-studio/rfcs/RFC0039-*.md, sdlc-studio/rfcs/RFC0042-*.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

reference-rfc.md's accept step 1 forbids acceptance while any Open Decision row is Open and step 2 requires a filled Decision section, but transition.py and validate.py contain no Open-Decisions check - the gate exists only in prose nobody is forced through (LL0027). Result: RFC0035/0037/0038/0039 are Accepted, decomposed and delivered while each carries only the boilerplate '| D1 | Act on this finding or keep status quo | Open |' as its decision record, and RFC0042 is Accepted with D2 (the close-owed detection mechanism, necessarily decided by shipped code) still Open. The rot is manufactured upstream: `file_finding.py`:447 still hard-codes that row into every RFC it files, the exact defect RFC0010 condemned in June - whose withdrawal cited fixes (CR0016/CR0021) that never touched the generator. rfc.py's advisory decide digest demonstrably did not stop the tranche. Six panel votes across the two source findings, five not-refuted (one argued RFC0010 intended the row as a gate - but six Accepted RFCs carrying it un-flipped shows the loop is broken either way). One coherent unit: enforce the gate, fix the generator, close the tranche rows.

## Impact

reference-rfc.md's accept step 1 forbids acceptance while any Open Decision row is Open and step 2 requires a filled Decision section, but transition.py and validate.py contain no Open-Decisions check - the gate exists only in prose nobody is forced through (LL0027).

## Acceptance Criteria

- [ ] transition.py refuses RFC -> Accepted while any Open Decision row is Open, with a recorded-override escape consistent with the gate doctrine
- [ ] `file_finding.py`'s RFC template derives decision rows from the finding's real options instead of emitting the content-free boilerplate row
- [ ] RFC0035/0037/0038/0039's D1 rows and RFC0042's D2 are closed with what actually shipped, with revision rows

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Raised |
