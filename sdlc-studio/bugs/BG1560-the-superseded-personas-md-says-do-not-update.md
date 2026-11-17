# BG1560: The superseded personas.md says do not update it, has been edited on three later dates and keeps a false date

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** sdlc-studio/personas.md, sdlc-studio/personas/index.md, sdlc-studio/personas/rowan-achterberg-skill-maintainer.md, tools/tests/test_persona_coherence.py
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

- [ ] **AC1** The behaviour described is corrected: The flat file sdlc-studio/personas.md opens with a banner declaring everything below it a historical record of a 2026-06-20 extraction and telling readers not...
- [ ] **AC2** The proposed fix lands, pinned by a test: Freeze the file for real.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
