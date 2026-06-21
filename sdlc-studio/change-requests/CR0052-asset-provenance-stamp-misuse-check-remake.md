# CR-0052: asset provenance stamp + misuse check + remake migration

> **Status:** Complete
> **Priority:** Medium
> **Type:** Feature
> **Requester:** Darren Benson
> **Date:** 2026-06-21
> **Affects:** scripts/artifact.py / file_finding.py (stamp on `new`), scripts/validate.py (misuse check), scripts/remake.py (new), reference-config.md (adoption cutoff), reference-outputs.md
> **Depends on:** CR0045 (deterministic `new`/`close`), CR0025 (remediation), CR0027 (adoption cutoff)
> **GitHub Issue:** --

## Summary

Make deterministic asset creation (CR0045) the **authoritative, enforceable** path: every
tool-created asset carries a **provenance stamp**; a check flags hand-created or malformed
assets with **remediation instructions** (advisory, behind an adoption cutoff so legacy
assets are not a wall of red); and a **`remake`** migration walks existing assets to the
current template + stamp without losing content. Turns "you can create assets with a tool"
into "assets are created right, and you can see and fix the ones that were not."

## Problem

CR0045 gives a deterministic `new`/`close`, but nothing distinguishes a correctly
tool-created asset from a hand-rolled one, nothing nudges an agent that bypassed the tool,
and there is no way to bring existing assets up to the current layout. Without these, the
deterministic path is optional and silently drifted-from.

## Proposed Changes

- **Stamp (in CR0045's `new`):** write one metadata line, e.g. `> **Created-by:** sdlc-studio new`,
  on every tool-created asset. Visible and machine-checkable; parser-ignored otherwise.
- **Misuse check (`validate`):** flag an asset that is missing the stamp or fails the
  layout/completeness guard, with a remediation message ("recreate with `/sdlc-studio new`
  or run `remake`"). **Advisory by default**, behind a `provenance.adopt_after` cutoff
  (reusing CR0027) so pre-adoption assets are exempt; opt-in blocking via config.
- **`remake` (new):** `remake [--type T] [--dry-run]` walks existing assets, normalises
  layout to the current template and adds the stamp - **content-preserving** (read-modify,
  never truncate; all fields/sections/prose retained), **idempotent**, **dry-run-first**.
- Document the authoritative-create flow + the cutoff in reference-outputs.md.

## Impact Assessment

| Module | Impact | Change Type |
| --- | --- | --- |
| scripts (new/artifact) | write the provenance stamp | Enhancement (CR0045) |
| scripts/validate.py | stamp/layout misuse finding + remediation, cutoff-exempt | Enhancement |
| scripts/remake.py | content-preserving layout+stamp migration | New |
| reference-config.md / reference-outputs.md | cutoff + authoritative-create docs | Modified |

### Breaking Changes

None. The misuse check is advisory + cutoff-gated; `remake` is opt-in and dry-run-able.

## Acceptance Criteria

- [x] `new` writes a provenance stamp; a tool-created asset is distinguishable from a hand-made one (check + eye).
- [x] `validate` flags un-stamped / malformed assets with a remediation message, is advisory by default, and exempts assets before `provenance.adopt_after`.
- [x] `remake --dry-run` reports what it would change; `remake` normalises layout + stamps, preserving all content, and is idempotent (a second run is a no-op).
- [x] Unit-tested incl. content-preservation + idempotence + cutoff exemption; independent critic APPROVE.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Autosprint (CR0052) | Complete - US0038: provenance.py stamp+check+remake; `new` stamps; created/closed by the tool (dogfood); critic REJECT->fixed (HIGH content-corruption in remake) |
| 2026-06-21 | Darren Benson | Raised - make deterministic creation authoritative: provenance stamp + misuse check (advisory, cutoff) + content-preserving remake migration |
