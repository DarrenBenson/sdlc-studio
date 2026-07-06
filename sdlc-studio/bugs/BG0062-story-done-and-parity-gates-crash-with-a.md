# BG0062: story Done and parity gates crash with a PyYAML RuntimeError instead of the block message on stdlib-only machines

> **Status:** Closed
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Severity:** Medium
> **Raised-by:** Sam Eriksson (QA amigo), repository review RV0006
> **Effort:** S

## Summary

When the depth-parity or Done-requires-verified gate fires on a machine without PyYAML,
`config.get` raises `RuntimeError` instead of the intended "blocked: ... Override with
--force" message, and `transition.cmd_set` does not catch it - so a `--ids` batch aborts
wholesale. The design contract is that runtime scripts degrade without PyYAML.

## Evidence

- `.claude/skills/sdlc-studio/scripts/transition.py:212-214` and `:222-225` -
  `import config; if config.get(root, "quality.depth_parity_gate"/"quality.done_requires_verified", ...)`.
- `.claude/skills/sdlc-studio/scripts/config.py:23-28` - `_yaml()` raises
  `RuntimeError("config loading needs PyYAML ...")`; `config.get` -> `load_config` -> `_yaml`
  unconditionally, even to read a default.
- `transition.py:305` - `cmd_set` catches only `(ValueError, FileNotFoundError)`.
- AGENTS.md soft-dependency table and `README:271` ("pure standard library, no pip installs")
  both state PyYAML is optional.

## Impact

The most load-bearing gate on the pipeline violates the stdlib-degradation contract exactly
when it has something to say: a blocked Done surfaces as a confusing dependency error rather
than the gate reason, and a batch transition aborts entirely instead of gating per id.

## Steps to Reproduce

1. On a machine without PyYAML installed, take a story with red executable ACs.
2. `transition.py set --id US0001 --status Done` (default `quality.done_requires_verified`).
3. The command raises the PyYAML RuntimeError rather than "US0001 -> Done blocked: ...".

## Proposed Fix

Route these config reads through `sdlc_md.project_override` (which already degrades to the
default), or wrap `config.get` in transition with a fallback to the documented default so the
gate message is produced. (The broader config-regime harmonisation is CR0180.)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Sam Eriksson (QA amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Sam Eriksson (QA amigo) | Evidence verified; corroborated by architecture and code-level legs |
| 2026-07-06 | Dani Okafor (Engineering amigo) | Fixed with a failing-first regression test on branch sprint/rv0006-bugfixes; transitioned to Closed |
