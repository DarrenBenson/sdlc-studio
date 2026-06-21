# CR-0054: review and reframe all help text around getting-started and autosprint

> **Status:** Complete
> **Priority:** High
> **Type:** Improvement
> **Date:** 2026-06-21

## Summary

Help currently steers toward the old human-driven, per-tool workflow. The focus is now autosprinting tranches of work. Reframe all help so the lead is getting-started + autosprint loops (autonomous tranches); demote the human-driven-tool detail to 'available if you want it'; keep the persona deep-dive content present and runnable by hand. Also fold in the self-audit's discoverability gaps.

## Acceptance Criteria

- [x] help/help.md leads with getting-started + the autosprint loop; every command (incl. pvd, gate, provenance, telemetry, new/close, skill-update, product reconcile) is listed in the catalogue
- [x] help/arguments.md + help/references.md cover the new commands/flags and reference-pvd/reference-skill-update
- [x] the human-driven-tool and persona deep-dive content is retained but secondary (runnable on demand, not the headline)
- [x] reviewed for consistency; the steer is getting-started + autosprint

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | audit | Raised |
| 2026-06-21 | Autosprint (CR0054) | Reframed help/help.md (autosprint-led), references.md, arguments.md; independent doc review APPROVE |
