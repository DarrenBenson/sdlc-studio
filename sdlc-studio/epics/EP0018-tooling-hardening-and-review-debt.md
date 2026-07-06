# EP0018: Tooling hardening and review debt

> **Status:** Draft
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new

## Summary

The maintainability layer of v4: the larger refactors the RV0006 bug sweep pointed at, plus
standing debt. Harmonise the three config failure regimes, route github_sync/verify_ac
through the shared discovery layer and unify the `--root` grammar, consolidate the two
archive implementations, clear the themed security- and code-quality debt, and finish the
batch-scaffold polish and context-tiering economy. Groups CR0180 (config regimes), CR0181
(shared discovery), CR0182 (archiver consolidation), CR0186 (security hardening debt), CR0187
(code-quality debt), CR0166 (batch scaffold polish), CR0179 (context tiering). Mostly
independent of the schema work; CR0180/CR0182 are smaller now that BG0062/BG0061 shipped.

## Story Breakdown

- [x] [US0076: Harmonise the config failure regimes with a warn on unhonoured override](../stories/US0076-harmonise-the-config-failure-regimes-with-a-warn.md)
- [x] [US0077: Route github_sync and verify_ac through shared discovery and unify root flag](../stories/US0077-route-github-sync-and-verify-ac-through-shared.md)
- [x] [US0078: Consolidate the two archive implementations on iter_tables](../stories/US0078-consolidate-the-two-archive-implementations-on-iter-tables.md)
- [x] [US0079: Security hardening: action pinning, installer integrity, sync redaction](../stories/US0079-security-hardening-action-pinning-installer-integrity-sync-redaction.md)
- [x] [US0080: Code-quality debt: docstrings, dedup, format json, complexity](../stories/US0080-code-quality-debt-docstrings-dedup-format-json-complexity.md)
- [x] [US0081: Batch scaffold wiring polish](../stories/US0081-batch-scaffold-wiring-polish.md)
- [x] [US0082: Context tiering: digest closed artefacts to bound token cost](../stories/US0082-context-tiering-digest-closed-artefacts-to-bound-token.md)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
