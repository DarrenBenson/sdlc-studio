# BG0304: 39 Done stories ship a literal {{role}} user-story block that no gate can see

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** High
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

The placeholder check scans only metadata lines and the Acceptance Criteria section, so the '**As a** {{role}}' scaffold artifact.py mints is invisible to every gate; 39 stories now Status: Done (including US0446, closed with full two-role paperwork) carry the unfilled block and validate.py reports zero placeholder findings, making the persona slot pure decoration on the delivery path.

## Steps to Reproduce

Evidence (`_check_placeholders`, lines 371-384; scaffold minted by artifact.py lines 379-380): US0446 line 3 'Status: Done', line 14 '**As a** {{role}}'; grep -rl '{{role}}' stories/*.md = 39 files, all Done; validate.py check emits 0 [placeholder] findings; artifact.py line 379 mints the scaffold.

## Proposed Fix

Extend `_check_placeholders` to flag {{...}} anywhere in the body outside code fences (or at minimum in the User Story block), and backfill the 39 Done stories' role blocks in a mechanical sweep.

## Acceptance Criteria

### AC1: a placeholder in the user-story block is flagged

- **Given** the defect as filed in Steps to Reproduce
- **When** the repair is in place
- **Then** the behaviour is the one the Proposed Fix describes, proven by a test written red before the fix
- **Proven by:** `pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::PlaceholderTests::test_user_story_block_placeholder_flagged`, written red before the fix and green after
- **Verified:** yes (2026-07-27, functional)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
| 2026-07-27 | Claude Fable 5 | Affects corrected to the fix footprint incl. its test file (BG0343: the filer wrote the evidence location) |
