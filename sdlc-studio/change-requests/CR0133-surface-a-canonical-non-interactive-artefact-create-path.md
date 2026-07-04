# CR-0133: surface a canonical non-interactive artefact-create path in every consuming project (no hand-allocated ids)

> **Status:** Proposed
> **Created:** 2026-07-04
> **Created-by:** sdlc-studio new
> **Priority:** High
> **Type:** Improvement
> **Affects:** .claude/skills/sdlc-studio/templates/agent-instructions.md, .claude/skills/sdlc-studio/help/bug.md, .claude/skills/sdlc-studio/help/cr.md, .claude/skills/sdlc-studio/reference-doctrine.md, .claude/skills/sdlc-studio/SKILL.md
> **Depends on:** -

## Summary

The skill's own philosophy is emphatic: **never hand-author `_index.md`, never hand-allocate ids**;
create artefacts with `scripts/artifact.py new`, which allocates a collision-free id, writes the
index row, and wires the epic. In the skill's home repo this is mandated by AGENTS.md and it works
cleanly. But a **consuming** project does not inherit that mandate legibly, and the gap has teeth.

Observed in the field (agent-crew, this session): the project's AGENTS.md points at
`/sdlc-studio bug create` - an **interactive** flow that cannot run in an autonomous / headless
session. With no non-interactive path surfaced, the agent fell back to hand-authoring the bug/CR
files and **hand-allocating BG/CR numbers by eyeballing the latest on disk** - precisely the
anti-pattern the philosophy forbids, and a real collision risk under concurrent sessions or a
rebase onto a branch that added ids. The deterministic tool existed the whole time; it simply was
not the visible path for that project.

The fix is not new capability - `artifact.py new` already does the right thing. The fix is
**making the deterministic path the obviously-correct one in every consuming project**, and making
the interactive skill flow delegate to it rather than be presented as the only door.

Proposed:

1. The shipped `templates/agent-instructions.md` (the file consuming projects adopt) names the
   **non-interactive** create command as *the* way to file a bug/CR/story - e.g.
   `python3 <skill>/scripts/artifact.py new --type bug --title "..."` - with the interactive
   `/sdlc-studio bug create` presented as a convenience wrapper, not the canonical path.
2. `help/bug.md` / `help/cr.md` lead with the non-interactive one-liner and state explicitly that
   ids and index rows are tool-allocated - hand-authoring either is an error.
3. A short "deterministic entry points" card (the 4-5 scripts an operator actually calls -
   `artifact.py new`, `reconcile.py detect|apply`, `transition.py`, `verify_ac.py`) is surfaced
   near the top of the router / doctrine, so the mechanical path is discoverable without spelunking
   the reference files.

## Acceptance Criteria

- [ ] `templates/agent-instructions.md` presents the non-interactive `artifact.py new` command as
      the canonical create path for bug/CR/story/epic, with the interactive flow noted as a wrapper
- [ ] `help/bug.md` and `help/cr.md` lead with the non-interactive one-liner and state that ids +
      index rows are tool-allocated (hand-authoring either is an error, with a one-line rationale:
      collision safety under concurrency/rebase)
- [ ] a "deterministic entry points" quick card (the scripts an operator calls, not the concepts)
      is reachable from the router or `reference-doctrine.md` in one hop
- [ ] the interactive `/sdlc-studio bug create` / `cr create` flows are documented as delegating to
      the same `artifact.py new` allocation (single id-allocation code path, no second hand path)
- [ ] `CHANGELOG.md` `[Unreleased]` entry ([[LL0004]])

## Out of Scope

- Building a new create command (the tool exists; this is discoverability + doctrine, not code).
- Retro-fixing already-hand-allocated ids in consuming projects.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | claude | Created via `new` (deterministic) |
