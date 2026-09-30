# BG0853: The agent-instructions template names the Claude Code skill path, so an AGENTS.md seeded for Codex, Copilot, Gemini or Cursor points at files that do not exist there

> **Status:** In Progress
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/templates/agent-instructions.md,.claude/skills/sdlc-studio/templates/agent-instructions.README.md,.claude/skills/sdlc-studio/scripts/init.py,.claude/skills/sdlc-studio/scripts/validate.py,.claude/skills/sdlc-studio/scripts/tests/test_validate.py,.claude/skills/sdlc-studio/scripts/project_upgrade.py,.claude/skills/sdlc-studio/scripts/tests/test_init.py,.claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py, changelog.d/BG0853.md
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

In the seeded agent-instructions files, stop naming one tool's install path: define a `<skill>` placeholder once in the template (listing the per-tool locations) and write `<skill>/reference-doctrine.md`, `python3 <skill>/scripts/gate.py`. Do NOT resolve init's `__file__` into the file: AGENTS.md is committed and shared, so one machine's absolute path would break every teammate on another tool. Extend the agent-instructions hygiene check (`validate.check_instructions`, which migrate already reports through) so an AGENTS.md/CLAUDE.md line naming a literal tool-specific skill install path is reported with its placeholder form, never rewritten. The check reads the text, not the machine, so every clone gets the same answer; a path that exists under the project root itself (a skill vendored in the repo, as in this repository) is not flagged. The other 13 docs are reference prose and can follow in the same change or a CR.

## Acceptance Criteria

- [ ] **AC1** Given init seeding a scratch project, when the seeded AGENTS.md is read, then it names no literal skill install path (`.claude/skills/sdlc-studio`, `.agents/skills/sdlc-studio`, or their `~/` forms): every skill path goes through the `<skill>` placeholder, which the file defines once with the per-tool locations - that one definition line is the only place a literal install path may appear, and the seeded CLAUDE.md (read only by Claude Code, where `.claude/skills` is correct) is exempt. Fails on: today's template line 22, wherever the running skill is installed - the test reads the seeded text, so it cannot pass vacuously from a checkout whose skill sits under .claude/skills
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init.py::AgentInstructionsSkillPathTests::test_seeded_agents_md_names_no_foreign_skill_path
  - **Verified:** yes (2026-09-30)
- [ ] **AC2** Given a workspace whose AGENTS.md names a literal tool-specific skill install path that is not under the project root, when `migrate.py --format json` runs, then a needs-a-human item names the line and its `<skill>` form, AGENTS.md is unchanged, and the answer is the same whether or not that path exists on the machine; a workspace vendoring the skill at that path under its own root gets no item, nor does CLAUDE.md naming a `.claude/skills` path, nor the placeholder's definition line. Fails on: silence, a rewrite, or a check that consults the machine's filesystem
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py::AgentInstructionsSkillPathTests::test_unresolvable_skill_path_is_reported_not_rewritten
  - **Verified:** yes (2026-09-30)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-29 | sdlc-studio | Filed |
| 2026-09-30 | sprint planning | Regroomed after goal-review round 78 (product, engineering and QA seats): placeholder mandated (resolving `__file__` commits one machine's path); AC1 made non-vacuous from this checkout [LC-002]; AC2 made machine-independent with a vendored-skill carve-out; validate.py and its test added to Affects. |
| 2026-09-30 | sprint planning | Finalised by hand after goal-review round 79 (two-round limit): the placeholder's definition line and CLAUDE.md are exempt from the no-literal-path rule (QA and engineering seats). |
