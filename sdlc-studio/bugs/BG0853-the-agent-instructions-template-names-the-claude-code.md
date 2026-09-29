# BG0853: The agent-instructions template names the Claude Code skill path, so an AGENTS.md seeded for Codex, Copilot, Gemini or Cursor points at files that do not exist there

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/templates/agent-instructions.md,.claude/skills/sdlc-studio/templates/agent-instructions.README.md,.claude/skills/sdlc-studio/scripts/init.py,.claude/skills/sdlc-studio/scripts/project_upgrade.py,.claude/skills/sdlc-studio/scripts/tests/test_init.py,.claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py, changelog.d/BG0853.md
> **Evidence:** Field report 2026-09-29; templates/agent-instructions.md:22; `grep -rl .claude/skills/sdlc-studio` over the skill's markdown returns 14 files
> **Created:** 2026-09-29
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-29T15:37:27Z

## Summary

Field report (v5.0.1 to v6.0.0 upgrade, skill installed for Copilot CLI via `--target agents`): templates/agent-instructions.md line 22 tells the reader to open `.claude/skills/sdlc-studio/reference-doctrine.md`. AGENTS.md is the file Codex, Copilot, Cursor and Gemini read, and on those tools the skill lives under `.agents/skills` (or `~/.agents/skills`), so for a user who installed only for them the path in the seeded AGENTS.md does not exist. The reporter's AGENTS.md carried three such lines (the doctrine read, `python3 ~/.claude/skills/sdlc-studio/scripts/artifact.py new ...` and `.../gate.py`). init.py describes these templates as tool-neutral starters. 14 markdown files in the skill carry the same literal path, including templates/agent-instructions.README.md, templates/audit-profiles/*.md, help/{audit,gate,lessons}.md and reference-{audit,config,scripts,agentic-lessons}.md. Nothing records where the skill was installed (no `SDLC_STUDIO_HOME` or equivalent), so neither the agent nor init can resolve it.

## Steps to Reproduce

Install with `install.sh --target agents` only (no Claude Code), run `init` in a scratch project, then test -e each skill path the seeded AGENTS.md names: the `.claude/skills/sdlc-studio/...` path does not resolve.

## Proposed Fix

In the seeded agent-instructions files, stop naming one tool's install path: either define a `<skill>` placeholder once in the template (listing the per-tool locations) and write `<skill>/reference-doctrine.md`, `python3 <skill>/scripts/gate.py`, or have init resolve the running skill's own folder (it knows `__file__`) and write that path. Extend the agent-instructions hygiene check that migrate already reports through so an AGENTS.md/CLAUDE.md line naming a skill path that does not resolve is reported (never rewritten). The other 13 docs are reference prose and can follow in the same change or a CR.

## Acceptance Criteria

- [ ] **AC1** Given init seeding a scratch project, when the seeded AGENTS.md is read, then it names no path under `.claude/skills/` unless the running skill is installed there. Fails on: the template's literal `.claude/skills/sdlc-studio/reference-doctrine.md`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init.py::AgentInstructionsSkillPathTests::test_seeded_agents_md_names_no_foreign_skill_path
- [ ] **AC2** Given a workspace whose AGENTS.md names a skill path that does not resolve, when `migrate.py --format json` runs, then a needs-a-human item names the line, and AGENTS.md is unchanged. Fails on: silence, or a rewrite
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py::AgentInstructionsSkillPathTests::test_unresolvable_skill_path_is_reported_not_rewritten

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-29 | sdlc-studio | Filed |
