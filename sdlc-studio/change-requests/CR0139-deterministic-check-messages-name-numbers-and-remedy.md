# CR-0139: deterministic-check findings should name the exact mismatch and the sanctioned remedy

> **Status:** Superseded
> **Created:** 2026-07-04
> **Created-by:** sdlc-studio remake (backfilled; filed from a consuming project's field report, 2026-07-04)
> **Priority:** Low
> **Type:** Improvement
> **Affects:** scripts/reconcile.py, scripts/validate.py, help/reconcile.md
> **Depends on:** -
> **Superseded by:** CR-0132

## Summary

> **Superseded (2026-07-04, operator-approved at sprint planning).** Same defect class as
> CR-0132 (self-diagnosing check findings); both ACs folded into CR-0132's criteria list.

Two deterministic checks report that something is wrong without saying what, so the operator loop
spends a diagnosis cycle the check has already paid for internally:

- **`reconcile detect` count-mismatch is opaque.** It reports `count-mismatch cr: recompute the
  summary counts from the index rows` with `id: null` - no status token, no numbers. The check has
  already computed rows-by-status and summary-by-status; in the field run the operator had to dump
  `--format json` and hand-diff census vs rows vs summary to find one token off by one
  (`Proposed: rows=5, summary=4`).
- **`validate` status-vocab errors hide the extension mechanism.** A project with an established
  extra status (14 artifacts using `Implemented`) gets 17 errors reading "not one of the allowed cr
  statuses (...)" with no mention that `.config.yaml` `status_vocab.<type>` exists precisely for
  this. The natural (wrong) reading is "rewrite 14 historical artifacts"; the sanctioned fix is one
  config stanza, discoverable only by reading `lib/sdlc_md.py`.

Same principle as the conformance failure's inline `REMEDY_*` strings, which name both whole-batch
levers and made that failure self-serving in the same field run: a finding should carry its own
diagnosis and the shortest sanctioned path to green.

## Acceptance Criteria

- [ ] `reconcile detect` count-mismatch names the artifact type, each mismatched status token and
      both numbers (for example `cr: Proposed rows=5 summary=4`), in text and JSON output
- [ ] `validate` status-vocab errors append the extension hint (for example: `or declare a project
      status via .config.yaml status_vocab.cr - see reference-config.md`)
- [ ] unit tests pin both message shapes; `CHANGELOG.md` `[Unreleased]` ([[LL0004]])

## Out of Scope

- Changing what either check enforces (messages only).
- Auto-applying either remedy.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | field | Filed from a consuming project's closing gate (one diagnosis cycle per opaque finding) |
| 2026-07-04 | claude | Superseded by CR-0132 (operator-approved merge at sprint planning); both ACs carried over verbatim |
