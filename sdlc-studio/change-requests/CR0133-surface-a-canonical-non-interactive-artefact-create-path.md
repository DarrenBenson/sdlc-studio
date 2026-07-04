# CR-0133: surface the deterministic toolbox so an agent reaches for the right script (map tasks to scripts, not just prose)

> **Status:** Approved
> **Created:** 2026-07-04
> **Created-by:** sdlc-studio new
> **Priority:** High
> **Type:** Improvement
> **Affects:** .claude/skills/sdlc-studio/SKILL.md, .claude/skills/sdlc-studio/reference-doctrine.md, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/templates/agent-instructions.md, .claude/skills/sdlc-studio/help/bug.md, .claude/skills/sdlc-studio/help/cr.md
> **Depends on:** -

## Summary

> **Broadened (2026-07-04).** First filed as "surface the canonical create path"; a session
> retrospective showed the problem is the *whole toolbox*, not just create. Rescoped.

The dominant finding from driving the skill end-to-end this session: **the tools are comprehensive
but an agent does not reach for them.** The suite has 40+ deterministic scripts
(`reference-scripts.md` documents 62 references), yet across a multi-task session the agent used
about two of them - and repeatedly hand-did work a script already automates:

- hand-authored six bug files and **hand-allocated the ids** - `file_finding.py` ("Deterministic
  Bug/CR/RFC finding filer") and `next_id.py` do exactly this, collision-safe;
- hit reconcile's `count-mismatch`, ran the suggested `apply` (which did not clear it), and
  concluded it was a "structural quirk" - `validate.py check` names the cause in one line, but was
  never run;
- introduced house-style violations that a linter should hold.

Root cause is **discoverability + orchestration**, not capability. The always-loaded router
(`SKILL.md`) names only a handful of scripts by filename; the full catalogue (`reference-scripts.md`)
loads only under the row "Invoking skill internals" - you find it only if you already know you want
internals. Crucially, the Progressive Loading Guide maps *task -> reference-`*`.md* (prose to read),
**not** *task -> script to run*. So an agent reads prose and hand-does what a script would do - the
exact anti-pattern the philosophy forbids ("never hand-author `_index.md` / hand-allocate ids").

The most acute instance is artefact creation in a **consuming** project: the adopted AGENTS.md points
at the interactive `/sdlc-studio bug create`, which cannot run headless, so the agent falls back to
hand-authoring - even though `artifact.py new` is right there. Fixing creation is necessary but not
sufficient; the general fix is to make the mechanical path the visible default for *every* task.

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

- [ ] the always-loaded router (`SKILL.md`) carries a compact **task -> script** map (or a one-hop
      pointer to it) for the mechanical operations an agent performs - create, reconcile, validate,
      transition, verify, find/file - so the deterministic path is visible without loading internals
- [ ] the Progressive Loading Guide rows for mechanical tasks name the **script to run**, not only
      the reference prose to read (e.g. "filing a finding -> `file_finding.py`", not only
      `reference-audit.md`)
- [ ] `templates/agent-instructions.md` presents the non-interactive `artifact.py new` as the
      canonical create path for bug/CR/story/epic in consuming projects, with the interactive
      `/sdlc-studio ... create` noted as a wrapper that delegates to the same allocation
- [ ] `help/bug.md` and `help/cr.md` lead with the non-interactive one-liner and state that ids +
      index rows are tool-allocated (hand-authoring either is an error - collision safety under
      concurrency/rebase)
- [ ] a "deterministic entry points" quick card (the scripts an operator/agent actually calls) is
      reachable from the router or `reference-doctrine.md` in one hop
- [ ] `CHANGELOG.md` `[Unreleased]` entry ([[LL0004]])

## Out of Scope

- Building new capability - the scripts exist; this is discoverability, routing, and doctrine.
- Retro-fixing already-hand-allocated ids in consuming projects.
- Auto-running scripts on the agent's behalf (this makes them discoverable; the agent still chooses).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | claude | Created via `new` (deterministic) |
| 2026-07-04 | claude | Broadened from "canonical create path" to "surface the whole toolbox" after a session used ~2 of 40+ scripts; retitled + rescoped |
