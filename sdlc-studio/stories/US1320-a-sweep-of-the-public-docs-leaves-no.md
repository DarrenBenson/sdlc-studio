# US1320: A sweep of the public docs leaves no generic Claude Code or Anthropic requirement, INSTALL.md links the harness page, and a guard keeps the public docs that way

> **Status:** Ready
> **Risk-class:** standard
> **Delivers:** CR0742
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** docs/INSTALL.md, docs/why-sdlc-studio.md, tools/tests/test_harness_neutral_docs.py, changelog.d/US1320.md
> **Epic:** EP0377
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** A sweep of the public docs leaves no generic Claude Code or Anthropic requirement, INSTALL.md links the harness page, and a guard keeps the public docs that way
**So that** CR0742 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: No public document says Claude Code or Anthropic is required

- **Given** README.md, every page under docs/, llms.txt, package.json, the SKILL.md front matter, the skill's help pages, AGENTS.md, CONTRIBUTING.md, SUPPORT.md and SECURITY.md
- **When** the guard scans them for "Claude Code skill", "Claude-Code-only", and statements that Claude Code, Claude or Anthropic is required
- **Then** it finds none, and a copy with one such phrase planted is refused by name. Fails on: any public page carrying one
- **Verify:** pytest tools/tests/test_harness_neutral_docs.py::HarnessNeutralDocsTests::test_no_public_document_says_claude_code_or_anthropic_is_required

### AC2: INSTALL.md installs a skill, not a Claude Code skill, and links the harness page

- **Given** `docs/INSTALL.md`
- **When** its quick install and its harness section are read
- **Then** the quick install no longer calls the default install "the Claude Code skill" and the page links `docs/harnesses.md`. Fails on: the old wording, or the link missing
- **Verify:** pytest tools/tests/test_harness_neutral_docs.py::HarnessNeutralDocsTests::test_install_md_is_neutral_and_links_the_harness_page

### AC3: The why page states the agentic fallback

- **Given** `docs/why-sdlc-studio.md`'s agentic-execution line
- **When** it is read
- **Then** it says what runs in a harness without sub-agents. Fails on: the line naming Claude Code with no fallback
- **Verify:** pytest tools/tests/test_harness_neutral_docs.py::HarnessNeutralDocsTests::test_the_why_page_states_the_agentic_fallback

## Notes

- Land last: the guard scans files US1315, US1318 and US1319 change. Release notes are a record of what shipped: leave them, unless one makes a generic requirement claim.
- Harness-specific instructions stay where they are (for example the INSTALL.md table rows and AGENTS.md's CLAUDE.md import line).
- LC-019 applies (new test file).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Created via `new` (deterministic) |
