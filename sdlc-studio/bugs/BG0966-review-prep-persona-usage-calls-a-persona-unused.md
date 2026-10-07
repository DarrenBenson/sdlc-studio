# BG0966: review_prep persona_usage calls a persona unused unless its file's H1 appears verbatim in prd.md - stories, CRs and consult logs are never read

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/review_prep.py, .claude/skills/sdlc-studio/scripts/tests/test_review_prep_persona_usage.py, .claude/skills/sdlc-studio/scripts/tests/test_review_prep.py, changelog.d/BG0966.md
> **Evidence:** Found running a consuming project on the installed skill 6.1.0, 2026-10-07; confirmed by reading the code at sdlc-studio main fb1ce886. There, all 6 personas reported unused; real references - the operator persona linked from 24 stories and 1 CR, Cora Wells from 9 stories / 4 epics / 21 CRs, the implementer seat from 19 stories.
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T12:36:35Z

## Summary

`persona_usage` (`review_prep.py` ~124-166) treats a persona as referenced only if the persona file's H1 string is a literal substring of prd.md. H1s such as 'Cora (Generic AI-Agent Persona U+2014 represents the 10-agent fleet)' cannot appear verbatim in a PRD, and the check never scans stories, CRs, epics or consult logs - where `### Persona Reference` sections, `Persona:` headers and path links to the persona files actually live. The unified review's Persona leg then starts from a false 'N of N unused'.

## Steps to Reproduce

A project whose stories link `personas/<name>.md` and name the persona in `### Persona Reference`, while the PRD names it informally. Run `review_prep.py prep` -> every persona listed unused.

## Proposed Fix

Count a persona referenced when its file path, file stem, or display name (not the decorated H1) appears in the PRD, stories, CRs, epics or the persona's consult log; report the reference count per persona so 'thin' and 'unused' are told apart.

## Acceptance Criteria

- [ ] **AC1** A persona linked by path from a story is not reported unused
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_review_prep_persona_usage.py -k path_link_counts
- [ ] **AC2** A persona named only by display name in a CR is not reported unused
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_review_prep_persona_usage.py -k display_name_counts
- [ ] **AC3** A persona referenced nowhere is still reported unused
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_review_prep_persona_usage.py -k unreferenced_still_unused

## Triage

- Reproduced at 8b844a80 by the code path: `persona_usage` reads only prd.md (review_prep.py:134). Already in the code since v1.8.0; not a regression. The em dash quoted from the persona H1 is spelled U+2014 so the house-style lane passes.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | Claude Opus 5.5 | Filed |
| 2026-10-07 | Claude Opus 5.5 (triage) | Triaged: reproduced at 8b844a80, not a regression, consuming-project name generalised for the neutrality lane; changelog fragment added to Affects |
