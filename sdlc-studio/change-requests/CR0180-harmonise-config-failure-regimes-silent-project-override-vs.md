# CR-0180: Harmonise config failure regimes: silent project_override vs fail-loud cutoff vs PyYAML crash

> **Status:** Complete
> **Size:** M
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic (v4 breakdown):** [EP0018](../epics/EP0018-tooling-hardening-and-review-debt.md)
> **Priority:** Medium
> **Type:** Improvement
> **Raised-by:** Sam Eriksson (QA amigo), repository review RV0006
> **Effort:** M

## Summary

Config handling has three inconsistent regimes: silent-default (`sdlc_md.project_override`),
fail-loud (`parse_cutoff`/`ConventionsError`), and hard-crash (`config.py` raising on missing
PyYAML). The README's "no pip installs" claim is false for the config/gate-policy paths.

## Motivation

An operator's declared conventions can be silently ignored - a custom status declared in
`.config.yaml` reverts to default when PyYAML is missing or the YAML is malformed, so
reconcile then emits a count-mismatch whose fix text tells the user to declare the status they
already declared. The one visible failure surfaces as a misleading PyYAML dependency error in
the middle of a Done transition (BG0062). This contradicts the project's own fail-loud lesson
(LL0008) applied one screen away in the same module.

## Scope

**In scope**

- `sdlc_md.project_override` (`lib/sdlc_md.py:333-340`) emits a one-line stderr warning when a
  `.config.yaml` exists but cannot be honoured (no PyYAML / parse error), instead of silently
  returning the default.
- Decide and document one policy for config-driven behaviour: either vendor a minimal
  YAML-subset parser for the override file so it works stdlib-only, or amend README/AGENTS.md
  to state PyYAML is required for config-driven behaviour (and keep the core pipeline
  stdlib-only).
- BG0062's transition-gate crash is fixed under this CR's umbrella or references it.

**Out of scope**

- Replacing YAML as the config format.
- The `parse_cutoff`/`ConventionsError` fail-loud paths (they are already correct).

## Acceptance Criteria

- [ ] A `.config.yaml` present but unreadable (no PyYAML or malformed) produces a visible
      one-line diagnostic, not a silent revert (test both conditions).
- [ ] The README/AGENTS.md dependency claim matches reality: either config works stdlib-only,
      or the docs state PyYAML is needed for config-driven behaviour.
- [ ] The three regimes are documented as one coherent policy in `reference-config.md`.
- [ ] BG0062 (Done gate PyYAML crash) is resolved or explicitly carried by this CR.

## Dependencies

| Artefact | Relationship |
| --- | --- |
| BG0062 | Same root cause (config.get requires PyYAML on a gate path); fix together |
| CR0180-CR0185 (RV0006 set) | Sibling review follow-ups |

## Risk

Vendoring a YAML subset risks silently mis-parsing valid-but-unusual YAML - worse than the
current crash. If chosen, restrict it to the documented override subset and fail loud on
anything outside it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Sam Eriksson (QA amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Sam Eriksson (QA amigo) | Full scope drafted from RV0006 architecture leg |
| 2026-07-08 | sweep-close (backlog reconciliation) | Delivered via US0076, already Done; CR status was never cascaded to Complete -> closed |
