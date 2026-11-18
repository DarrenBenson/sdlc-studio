# US1318: The README first screen leads with harness-agnostic and human in the lead, names the six harnesses in one alphabetical table, links the harness and enterprise pages, and moves the sponsorship line to Acknowledgements, no longer than today

> **Status:** Done
> **Risk-class:** standard
> **Delivers:** CR0742
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** README.md, tools/tests/test_readme_front_door.py, changelog.d/US1318.md
> **Epic:** EP0377
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The README first screen leads with harness-agnostic and human in the lead, names the six harnesses in one alphabetical table, links the harness and enterprise pages, and moves the sponsorship line to Acknowledgements, no longer than today
**So that** CR0742 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The first screen names the six harnesses and links the two new pages

- **Given** `README.md`
- **When** its first screen (the text before the second `##` heading) is read
- **Then** it leads with harness-agnostic and human in the lead, names Claude Code, Codex, Cursor, Gemini CLI, GitHub Copilot and opencode, and links `docs/harnesses.md` and `docs/enterprise.md`, both of which exist. Fails on: a harness missing, either link missing, or a link to a page that does not exist
- **Verify:** pytest tools/tests/test_readme_front_door.py::ReadmeFrontDoorTests::test_the_first_screen_names_six_harnesses_and_links_the_two_pages
- **Verified:** yes (2026-11-18)

### AC2: One alphabetical harness table gives install, invocation and a verification command

- **Given** the README's install section
- **When** its harness table is parsed
- **Then** there is one table, its rows in alphabetical order, and each row, GitHub Copilot's included, gives the install location, the invocation and a command that verifies the install. Fails on: a second harness table, rows out of order, or a row with no verification command
- **Verify:** pytest tools/tests/test_readme_front_door.py::ReadmeFrontDoorTests::test_the_harness_table_is_alphabetical_with_a_verification_command
- **Verified:** yes (2026-11-18)

### AC3: Acknowledgements carries the sponsorship and says Anthropic products are not required

- **Given** the README
- **When** it is searched for the sponsorship line
- **Then** the line sits under an Acknowledgements heading that also says SDLC Studio does not require Anthropic products, and the README never says "Claude Code skill". Fails on: the sponsorship line outside Acknowledgements, or the statement missing
- **Verify:** pytest tools/tests/test_readme_front_door.py::ReadmeFrontDoorTests::test_acknowledgements_carries_the_sponsorship_and_no_anthropic_requirement
- **Verified:** yes (2026-11-18)

### AC4: The README is no longer than before

- **Given** the README's word count as `wc -w` counts it
- **When** it is compared with 1,500, the count at 59b649d4
- **Then** it is at most 1,500 and the existing front-door tests still pass. Fails on: a README over 1,500 words
- **Verify:** pytest tools/tests/test_readme_front_door.py::ReadmeFrontDoorTests::test_the_readme_is_no_longer_than_before_cr0742
- **Verified:** yes (2026-11-18)

## Notes

- Land after US1316 and US1317, whose pages the first screen links.
- Keep harness-specific instructions in the install section; keep every existing front-door assertion green.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Created via `new` (deterministic) |
