# BG1560: The superseded personas.md says do not update it, has been edited on three later dates and keeps a false date

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 2
> **Affects:** sdlc-studio/personas.md, sdlc-studio/personas/index.md, sdlc-studio/personas/rowan-achterberg-skill-maintainer.md, tools/tests/test_persona_coherence.py, changelog.d/BG1560.md
> **Evidence:** audit AUDIT-2026-11-17, project profile, personas lens, survived 2 of 3 refute votes; observed at sdlc-studio/personas.md Banner (lines 11-20), metadata block (lines 22-25), and the Skill Maintainer section
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:29:25Z

## Summary

The flat file sdlc-studio/personas.md opens with a banner declaring everything below it a historical record of a 2026-06-20 extraction and telling readers not to update it, and the persona registry says the file is not maintained. Its git history shows content commits on 2026-07-29 (two) and 2026-11-01, after the supersession on 2026-07-27, and its Skill Maintainer section now carries present-tense operating detail that did not exist in June, such as the forward-port mirror and its check flag. The header still reads Version 2.0.0 and Last Updated 2026-06-20. The file is therefore neither the untouched record its banner claims nor a maintained page: 258 lines that duplicate the subject of the skill maintainer's card under a date that is false. A reader cannot tell which statements in it are historical and which were corrected later.

## Steps to Reproduce

1. Open sdlc-studio/personas.md and read the banner at lines 11 to 20: it says the content is historical and must not be updated.
2. Read the metadata block at lines 22 to 25: Version 2.0.0, Last Updated 2026-06-20.
3. Run git log on that file with a short date format: commits c24be54b (2026-11-01), eacd23a3 and 3c3eb69a (both 2026-07-29) follow the supersession commit cde15b12 of 2026-07-27.
4. Read the Skill Maintainer section and find present-tense detail on the forward-port mirror and a D0379 pointer to the persona card, neither of which existed on 2026-06-20.
5. Open sdlc-studio/personas/index.md at line 57: the registry says the flat file is not maintained.

## Proposed Fix

Freeze the file for real. Move any post-June operating detail that the skill maintainer's card lacks into that card, then cut the flat file down to its banner and a pointer to the registry, leaving the 2026-06-20 extraction to git history; correct the header so it no longer carries a false Last Updated date. Keep the registry's Superseded note in step with what the file now is. Add a check to tools/tests/`test_persona_coherence.py` that a flat personas file carrying the legacy banner holds no persona sections below it, so the frozen claim cannot drift again.

## Acceptance Criteria

- [ ] **AC1** Given sdlc-studio/personas.md, when it is read, then it holds its legacy banner and a pointer to the registry and no persona section below them, and its header carries no Last Updated date earlier than its latest content change. Fails on: persona sections surviving under a banner that says the file is frozen, or the 2026-06-20 date kept over later edits.
  - **Verify:** pytest tools/tests/test_persona_coherence.py::LegacyAppendixTests::test_the_frozen_flat_file_holds_no_persona_sections
- [ ] **AC2** Given the operating detail the flat file's Skill Maintainer section gained after the supersession, the forward-port mirror and its check flag among it, when the skill maintainer's card is read, then the card states that detail, and the registry's Superseded note describes the flat file as the banner and pointer it now is. Fails on: detail deleted from the flat file and present nowhere, or a registry note describing a file that no longer exists in that form.
  - **Verify:** pytest tools/tests/test_persona_coherence.py::LegacyAppendixTests::test_the_card_carries_the_detail_the_flat_file_dropped
- [ ] **AC3** Given a fixture flat personas file carrying the legacy banner with a persona section added below it, when the same check runs, then the section is reported; a fixture holding the banner and pointer alone passes. Fails on: a frozen claim that can drift again unnoticed.
  - **Verify:** pytest tools/tests/test_persona_coherence.py::LegacyAppendixTests::test_a_persona_section_under_the_banner_is_reported

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because it is what is left of a fix already shipped. personas.md is a superseded flat file whose banner is stale; the registry already says it is unmaintained and nothing reads it. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
