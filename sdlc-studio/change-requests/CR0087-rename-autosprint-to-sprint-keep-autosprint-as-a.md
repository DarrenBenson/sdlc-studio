# CR-0087: rename autosprint to sprint, keep autosprint as a deprecated alias

> **Status:** Proposed
> **Created:** 2026-06-24
> **Created-by:** sdlc-studio new
> **Priority:** High
> **Type:** Improvement

## Summary

**WS0 of RFC0019 (do first). Estimate: 3 points.** Rename the command `autosprint` -> `sprint`.
The command is now the whole sprint lifecycle (`--goal plan`/`design`/`done`), not just
autonomous delivery; autonomy is the existing `--autonomous` flag, not the name. `sprint` is
cleaner and standard agile vocabulary. Keep `autosprint` as a **deprecated alias** so nothing
breaks. Done first so the rest of the sprint's docs are written against the final name.

## Scope

- Rename `scripts/autosprint.py` -> `scripts/sprint.py` (update the test module + every
  sibling import); `reference-autosprint.md` -> `reference-sprint.md`;
  `help/autosprint.md` -> `help/sprint.md`.
- Update the **live** command surface to say `sprint`: SKILL.md rows, `help/help.md`,
  `help/getting-started.md`, `templates/agent-instructions.md`, `reference-verify.md`,
  and the `--goal` ladder.
- **Alias:** `/sdlc-studio autosprint ...` still resolves (NL + a thin command shim), with a
  one-line deprecation note pointing at `sprint`.
- **Do not rewrite history:** CHANGELOG, closed CRs, RFC0001 keep "autosprint" (historical).

## Acceptance Criteria

- [ ] `/sdlc-studio sprint ...` is the canonical command; `scripts/sprint.py` is the script
      and its tests pass under the new name
- [ ] `/sdlc-studio autosprint ...` still works as a deprecated alias (NL + shim), emitting a
      deprecation pointer to `sprint`; no behaviour change
- [ ] all live docs (SKILL rows, help, reference-sprint, getting-started, agent-instructions,
      reference-verify) say `sprint`; the doc-coverage gate passes for the renamed command
- [ ] historical records (CHANGELOG, closed CRs, RFC0001) are left unchanged
- [ ] `npm run lint && npm test && gate` green; CHANGELOG `[Unreleased]` entry (LL0004)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | sdlc | Created via `new` (deterministic) |
