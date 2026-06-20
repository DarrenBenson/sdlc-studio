# CR-0027: per-project status vocab + conformance adoption cutoff

> **Status:** Complete
> **Priority:** High
> **Type:** Feature
> **Requester:** agent-crew (relayed) - consuming-project feedback
> **Date:** 2026-06-20
> **Affects:** scripts/lib/sdlc_md.py, scripts/conformance.py, scripts/validate.py, scripts/reconcile.py, scripts/status.py, scripts/audit.py, scripts/integrity.py, scripts/autosprint.py, scripts/resume.py, scripts/rfc.py, templates/config-defaults.yaml
> **Depends on:** CR0008 (config), BG0020/BG0021 (parser)
> **GitHub Issue:** --

## Summary

A consuming project (agent-crew) reported two ways the skill imposes its own reality
on a project that differs. Both are answered by letting a project declare itself in
`sdlc-studio/.config.yaml`:

1. **Status vocabulary is closed.** A project that genuinely uses extra statuses
   (e.g. `Gated`) parses those rows as `Unknown`, so reconcile/validate/conformance
   cannot reason about them. Now `status_vocab.<type>` extends the base vocabulary
   per type. `Blocked` (a universal lifecycle state, already valid for epics/CRs/bugs)
   is added to the base story vocabulary outright.
2. **Conformance judges all history.** A project that turns the gate on partway has
   hundreds of legacy stories permanently reported non-conformant (agent-crew: ~414).
   Now `conformance.adopt_after: USnnnn` exempts pre-adoption stories - the discipline
   applies forward, not retroactively.

## Proposed Changes

### Item 1: config-extensible status vocab + `Blocked`

**Priority:** High **Effort:** Medium

New `sdlc_md.status_vocab(type_, repo_root)` = base + project `status_vocab.<type>`
extensions, read via a new self-contained, fully-degrading `sdlc_md.project_override`
(no file / no PyYAML / malformed YAML all fall back to base; never raises on the
parser-critical path). 13 call sites migrated off the raw `STATUS_VOCAB.get`.

### Item 2: conformance adoption cutoff

**Priority:** High **Effort:** Low

`detect_conformance` reads `conformance.adopt_after`; stories with a lower id are
`exempt` (reported, conformant, never counted non-conformant). New summary key
`exempt`; text output shows "N exempt (pre-adoption)".

## Impact Assessment

| Module | Impact | Change Type |
| --- | --- | --- |
| scripts/lib/sdlc_md.py | `project_override` + `status_vocab` + `Blocked` in base | New |
| scripts/conformance.py | `adopt_after` cutoff + `exempt` summary | Modified |
| 8 other scripts | migrate to `status_vocab(type_, root)` | Modified |
| templates/config-defaults.yaml | document `status_vocab` + `conformance.adopt_after` | Modified |

### Breaking Changes

`conformance` summary gains an `exempt` key (additive). `Blocked` becomes a valid
story status everywhere (was previously flagged). No project migration needed.

## Acceptance Criteria

- [x] `status_vocab(type_, root)` returns base + `.config.yaml` `status_vocab.<type>`; `Blocked` is in the base story vocab; `project_override` degrades on missing/no-PyYAML/malformed/type-confused config without raising.
- [x] All 13 vocab call sites pass the repo root; our own repo is unaffected (conformance 23/23, drift 0).
- [x] `conformance.adopt_after: USnnnn` exempts lower-id stories (reported, not counted non-conformant; cmd exits 0 when all failing units are exempt).
- [x] Unit-tested (vocab base/extension/degradation, cutoff exempt/judge/all-exempt); independent critic APPROVE.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (CR0027) | Complete - US0024 (vocab + Blocked) + US0025 (adopt_after); critic APPROVE, LOW follow-ups applied (id_number reuse + degradation tests) |
| 2026-06-20 | agent-crew (relayed) | Raised - closed status vocab (Gated) + permanent conformance noise on legacy stories |
