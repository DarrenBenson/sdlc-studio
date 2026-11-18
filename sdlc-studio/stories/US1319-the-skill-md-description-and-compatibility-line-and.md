# US1319: The SKILL.md description and compatibility line and llms.txt are harness-neutral, and --agentic states its fallback outside Claude Code

> **Status:** Done
> **Risk-class:** standard
> **Delivers:** CR0742
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/SKILL.md, .claude/skills/sdlc-studio/help/epic.md, llms.txt, tools/tests/test_skill_metadata_neutral.py, changelog.d/US1319.md
> **Epic:** EP0377
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The SKILL.md description and compatibility line and llms.txt are harness-neutral, and --agentic states its fallback outside Claude Code
**So that** CR0742 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: SKILL.md's description and compatibility line require no single harness

- **Given** the SKILL.md front matter
- **When** its `description` and `compatibility` fields are read
- **Then** neither names a harness as required, and `compatibility` says `--agentic` runs its waves in parallel where the harness has sub-agents and runs the same stories one at a time elsewhere. Fails on: "Claude-Code-only", or any harness named as a requirement
- **Verify:** pytest tools/tests/test_skill_metadata_neutral.py::SkillMetadataNeutralTests::test_skill_md_requires_no_single_harness
- **Verified:** yes (2026-11-18)

### AC2: llms.txt names the six harnesses and links the two new pages

- **Given** `llms.txt`
- **When** its summary and Docs list are read
- **Then** the summary names Claude Code, Codex, Cursor, Gemini CLI, GitHub Copilot and opencode with none first by default, and the Docs list links `docs/harnesses.md` and `docs/enterprise.md`. Fails on: a harness missing, or either link missing
- **Verify:** pytest tools/tests/test_skill_metadata_neutral.py::SkillMetadataNeutralTests::test_llms_txt_names_six_harnesses_and_links_the_new_pages
- **Verified:** yes (2026-11-18)

### AC3: epic help states the --agentic fallback

- **Given** `help/epic.md`'s option table
- **When** its `--agentic` row is read
- **Then** it says what happens in a harness without sub-agents. Fails on: the row with no fallback
- **Verify:** pytest tools/tests/test_skill_metadata_neutral.py::SkillMetadataNeutralTests::test_epic_help_states_the_agentic_fallback
- **Verified:** yes (2026-11-18)

## Notes

- Land after US1316 and US1317 (llms.txt links their pages). Keep every SKILL.md budget and trigger test green. The orchestrator runs `tools/forward-port.sh --yes` before the close; the builder does not.
- LC-019 applies (new test file).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Created via `new` (deterministic) |
