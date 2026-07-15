# BG0151: discovery_awaiting and migrate falsely flag old-flow CRs as un-refined - children_of ignores the legacy Change Request / Linked Epics linking

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** High
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/status.py, .claude/skills/sdlc-studio/scripts/migrate_v3.py
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Found dogfooding on the homelab project (old flow, `two_backlog.enforce` off, profile lite). A CR decomposed the OLD way carries its epics via cr-action linking - the epic has '> **Change Request:** CR-0001' and the CR a '## Linked Epics' table - NOT the new '> **Parent:** CR0001' / '> **Decomposed-into:**'. `children_of()` (lib/`sdlc_md)` reads only Parent: and a story's Epic:, so `children_of(`'CR0001') returns [] even though CR0001 is decomposed into EP0002/EP0003. Every feature built on `children_of` then misreports the CR as un-refined: status/hint `discovery_awaiting` says '24 await refinement/triage' (US0151/US0152), and migrate flags 12 CRs as needs-refine (this sprint) - all false positives, on the command that is supposed to be the honest upgrade front door. `reconcile.undecomposed_drift` is spared only because it is gated on `two_backlog_enforced` (homelab off); `discovery_awaiting` and `migrate_v3.migrate_sizing` call the primitive ungated.

## Steps to Reproduce

On a project that decomposes CRs via cr action (epic carries '> **Change Request:** CR-XXXX', no '> **Parent:**'), run status hint (or status pillars) and migrate. Observe `discovery_awaiting` counts the already-decomposed CRs as awaiting refinement, and migrate lists them under needs-refine. Reproduced on ../homelab: `children_of(`'CR0001')==[] while EP0002/EP0003 carry Change Request: CR-0001.

## Proposed Fix

Teach `children_of` the legacy back-links so a CR that is decomposed the old way is correctly seen as having children: an epic's '> **Change Request:** CR-XXXX' (and a story's originating link) makes it a child of that CR. That fixes all surfaces at the root (hint, status, migrate, and `undecomposed_drift` under enforce) for old-flow and migrating projects. Alternatively/additionally, gate the awaiting-refinement surfacing (`discovery_awaiting`; migrate's needs-refine) on `two_backlog_enforced` so an old-flow project is never nagged to refine - but teaching `children_of` is the correct fix since a decomposed CR genuinely has children. Add a fixture with old-style Change Request linking (the test suite only used new-style links, which is why this slipped).

Fixed: added `sdlc_md.change_request_ref` (reads an epic's `> **Change Request:**`) and folded it into `child_parent` as the most-specific-first fallback after `Parent:`/`Epic:`. Verified against ../homelab (read-only): `children_of('CR0001')` now returns EP0002/EP0003, `discovery_awaiting` dropped 24 -> 16 (the remainder genuinely childless), and `migrate` needs-refine dropped 12 -> 4 (the truly-undecomposed).

- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_two_backlogs.LinkPrimitiveTests.test_child_parent_reads_the_legacy_change_request_link tests.test_two_backlogs.LinkPrimitiveTests.test_children_of_and_awaiting_see_a_legacy_decomposed_cr

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Filed |
| 2026-07-15 | sdlc-studio | Root cause: children_of read only new-style links; fixed by teaching it the legacy Change Request epic->CR link; verified on ../homelab + regression tests |
