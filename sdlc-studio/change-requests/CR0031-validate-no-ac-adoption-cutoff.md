# CR-0031: validate `no-ac` honours the conformance adoption cutoff

> **Status:** Complete
> **Priority:** Medium
> **Type:** Improvement
> **Requester:** consuming repo A (consuming project, authored the fix)
> **Date:** 2026-06-20
> **Affects:** scripts/validate.py, scripts/tests/test_validate.py
> **Depends on:** CR0027 (the adoption cutoff + project_override it reuses)
> **GitHub Issue:** --

## Summary

A consuming project (consuming repo A) extended CR0027's adoption cutoff to `validate.py`:
a story whose id predates `.config.yaml` `conformance.adopt_after` is now exempt from
the `no-ac` error, just as it is from the conformance gate. Authored live in the
installed skill and back-ported here so it is preserved (a future forward-port would
otherwise clobber it). Reviewed and adopted.

## Problem

CR0027 stopped the conformance gate from flagging every legacy story, but `validate`'s
`no-ac` check still flagged each pre-adoption story missing an AC section - the same
wall-of-red, one check over.

## Proposed Changes

`_ac_exempt(rec, repo_root)` reads `conformance.adopt_after` (via `sdlc_md.project_override`)
and exempts a story whose `id_number` is below the cutoff from the `no-ac` error only.
Story-scoped (inside `if type_ == "story"`); fails safe toward judging on any
uncertainty (no repo_root / no cutoff / no PyYAML / malformed config / unparseable id).

## Impact Assessment

| Module | Impact | Change Type |
| --- | --- | --- |
| scripts/validate.py | `_ac_exempt` gate on the no-ac check | Modified |
| scripts/tests/test_validate.py | grandfather/judge/no-cutoff + degradation + boundary tests | Modified |

### Breaking Changes

None. Without a configured cutoff, every story is judged exactly as before.

## Acceptance Criteria

- [x] A pre-cutoff story is exempt from `no-ac`; a story at/after the cutoff is still flagged (exclusive boundary).
- [x] Exemption is story-scoped and applies to `no-ac` only - never to id-format/no-title/no-status/status-vocab, never to non-stories.
- [x] Fails safe: no config, no PyYAML, malformed config, or an unparseable id all judge the story (error fires).
- [x] Unit-tested (grandfather, judge, no-cutoff, malformed-config, at-cutoff); independent critic APPROVE.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (CR0031) | Complete - US0029: adopted consuming repo A's fix, back-ported + 2 fail-safe tests; critic APPROVE |
| 2026-06-20 | consuming repo A | Authored - extended the adoption cutoff to validate's no-ac check |
