# US1315: The GitHub About description, topics and package.json description name SDLC Studio a harness-agnostic Agent Skill, not a Claude Code skill

> **Status:** Ready
> **Risk-class:** standard
> **Delivers:** CR0742
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** package.json, sdlc-studio/change-requests/CR0742-harness-agnostic-and-enterprise-ready-documentation.md, tools/tests/test_package_metadata.py, changelog.d/US1315.md
> **Epic:** EP0377
> **Points:** 1
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The GitHub About description, topics and package.json description name SDLC Studio a harness-agnostic Agent Skill, not a Claude Code skill
**So that** CR0742 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: package.json describes a harness-agnostic Agent Skill

- **Given** `package.json` at the repository root
- **When** its `description` and `keywords` are read
- **Then** the description is "Harness-agnostic Agent Skill for governed software delivery, human in the lead. Works in GitHub Copilot, Claude Code, Cursor, Codex, Gemini CLI and opencode." and the keywords hold CR0742's ten topics. Fails on: the old "Claude Code skill" description, or a topic missing
- **Verify:** pytest tools/tests/test_package_metadata.py::PackageMetadataTests::test_the_description_and_keywords_are_harness_agnostic

### AC2: CR0742 records the exact About text and topics for the owner

- **Given** CR0742's Requested changes
- **When** the GitHub About description and topics are read from it
- **Then** the CR carries the description and the ten topics verbatim, and a `## Applied` note says whether `gh repo edit` applied them and when. Fails on: the text paraphrased, or no note of whether it was applied
- **Verify:** pytest tools/tests/test_package_metadata.py::PackageMetadataTests::test_cr0742_records_the_about_text_and_whether_it_was_applied

## Notes

- The About box and topics are repository settings, applied by the orchestrator with `gh repo edit` after review (the builder does not change live settings); the builder writes the `## Applied` note as "pending" and the orchestrator completes it.
- Topics are set to exactly CR0742's ten, replacing the current set (which includes `claude-code-skill`).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Created via `new` (deterministic) |
