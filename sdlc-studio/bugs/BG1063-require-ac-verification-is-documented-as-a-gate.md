# BG1063: `require_ac_verification` is documented as a gate that aborts the completion cascade on a failed verification, but no code reads it

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-verify.md, .claude/skills/sdlc-studio/reference-outputs.md, .claude/skills/sdlc-studio/scripts/constitution.py, .claude/skills/sdlc-studio/scripts/tests/test_retired_config_keys.py, changelog.d/BG1063.md, .claude/skills/sdlc-studio/scripts/tests/test_constitution.py
> **Evidence:** RV0028 finding PRD-2; config-defaults.yaml:98; reference-outputs.md:768; transition.py:1042-1049 reads `quality.done_requires_verified`.
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T07:49:39Z

## Summary

The PRD (prd.md:322, :599), reference-verify.md:290-296, reference-outputs.md:768 and templates/config-defaults.yaml:98 describe `require_ac_verification` as the switch that makes `artifact.py close` run `verify_ac` and abort the cascade on failure. A grep of the shipped scripts finds it only in a comment (constitution.py:13); artifact.py:1390-1415 `close` delegates to transition.transition with no such read. The live gate is `quality.done_requires_verified`. A key a user can set that changes nothing is the false-assurance class LL0008 names.

## Steps to Reproduce

`grep -rn require_ac_verification --include=*.py .claude/skills/sdlc-studio` -> only scripts/constitution.py:13, a comment. Set `require_ac_verification: false` in a fixture project's config and `artifact.py close` a story with a red Verify line -> the Done gate still refuses (it reads `quality.done_requires_verified`).

## Proposed Fix

Retire the key from templates/config-defaults.yaml and every reference that names it, pointing at `quality.done_requires_verified`; or wire it, if a separate switch is wanted.

## Acceptance Criteria

- [ ] **AC1** `require_ac_verification` is either read by the gate the documents say it switches or absent from config-defaults.yaml and every shipped reference
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retired_config_keys.py -k require_ac_verification_is_read_or_retired

## Impact

An operator who sets the documented key believes they changed a gate; nothing changes.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
