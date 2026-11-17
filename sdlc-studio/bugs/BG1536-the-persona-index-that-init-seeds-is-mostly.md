# BG1536: The persona index that init seeds is mostly dead: unfilled placeholders, unread sections and a broken link

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/templates/personas/persona-index-template.md, .claude/skills/sdlc-studio/scripts/tests/test_init.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, personas lens, survived 3 of 3 refute votes; observed at .claude/skills/sdlc-studio/templates/personas/persona-index-template.md Sections 'Team Personas', 'Stakeholder Personas', 'Consultation Defaults', 'Custom Personas', 'Usage', 'Persona Sources' and the final 'See reference-persona.md' line (lines 26-133)
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:23:45Z

## Summary

`init.py` seeds `sdlc-studio/personas/index.md` in every consuming project from `persona-index-template.md`. Only the Primary, Secondary and Negative headings of that template are read by anything, through `sdlc_md.persona_registry`. The other sections (Team Personas, Stakeholder Personas, Consultation Defaults, Custom Personas, Usage and Persona Sources, lines 26 to 133) are copied verbatim, leaving 32 literal placeholders in a project file, and no script or reference page reads any of those tables. The Team Personas section contradicts this repository's own index, which says the review seats are not personas. The closing link to `reference-persona.md` uses a relative path that, from the seeded location, resolves to the project root, where no such file exists. The template also offers three cast headings while `persona-template.md` declares six cast roles.

## Steps to Reproduce

1. Run `init.py` in an empty scratch project so that it seeds `sdlc-studio/personas/index.md`.
2. Open the seeded file and count the remaining double-brace placeholders: 32 are left unfilled.
3. Follow the closing link to `reference-persona.md` from the seeded file: it resolves two levels up, to the project root, where the file does not exist.
4. Search the skill's scripts and reference pages, excluding the template, for Consultation Defaults, Team Personas and Persona Sources: there is no reader.
5. Expected: a seeded index holding only what the registry reads, with no unfilled placeholder and no dead link. Actual: about 100 lines of unread scaffold with 32 placeholders and a link that resolves nowhere.

## Proposed Fix

Cut `persona-index-template.md` down to what is read: the cast headings the registry and `persona-template.md` agree on, plus a short pointer to where seats and stakeholders live. Remove the Team Personas, Stakeholder Personas, Consultation Defaults, Custom Personas and Persona Sources tables, and replace the relative link with the skill page's name in plain text so it cannot resolve to a missing file. Add a test to `test_init.py` that seeds the index in a fixture and asserts no placeholder remains, every Markdown link in it resolves or is absent, and every heading in it is one the registry reader recognises.

## Acceptance Criteria

- [ ] **AC1** Given an empty scratch project, when `init.py` seeds `sdlc-studio/personas/index.md`, then the seeded file holds no unfilled double-brace placeholder. Fails on: any literal placeholder left in a consuming project's index.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init.py::SeededPersonaIndexTests::test_the_seeded_index_holds_no_placeholder
- [ ] **AC2** Given the same seeded index, when its headings are read, then every one is a cast heading that `sdlc_md.persona_registry` recognises and `persona-template.md` declares, and the Team Personas, Stakeholder Personas, Consultation Defaults, Custom Personas and Persona Sources tables are absent. Fails on: a seeded section no script or reference page reads, or a cast role the template declares that the index cannot hold.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init.py::SeededPersonaIndexTests::test_every_seeded_heading_is_one_the_registry_reads
- [ ] **AC3** Given the same seeded index, when each Markdown link in it is resolved from the seeded location, then it reaches an existing file, or the page is named in plain text with no link. Fails on: the relative link to `reference-persona.md` resolving to the project root, where no such file exists.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init.py::SeededPersonaIndexTests::test_no_seeded_link_resolves_to_a_missing_file

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
