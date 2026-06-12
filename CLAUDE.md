# CLAUDE.md

@AGENTS.md

## Claude Code Specifics

- The skill live-reloads from `.claude/skills/sdlc-studio/` in this repo;
  edits to SKILL.md take effect mid-session.
- Invoke as `/sdlc-studio [type] [action]`; the skill is also
  model-invoked from its description.
- Plan-mode plan files (`~/.claude/plans/`) are managed via
  `/sdlc-studio plan list|archive` - see
  `.claude/skills/sdlc-studio/reference-plan-files.md`.
