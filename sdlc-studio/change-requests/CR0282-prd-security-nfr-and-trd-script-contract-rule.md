# CR-0282: PRD security NFR and TRD script-contract rule 6/threat model deny the shipped network surface: a default-on GitHub phone-home via urllib and sprint plan's git fetch

> **Status:** In Progress
> **Decomposed-into:** EP0071
> **Priority:** High
> **Type:** docs
> **Size:** S
> **Affects:** sdlc-studio/prd.md, sdlc-studio/trd.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

prd.md:370 ('No network calls except gh and the tools a project's Verify lines invoke'), trd.md rule 6 (lines 245-246, 'No network access except the gh CLI wrapper in `github_sync.py`') and the trd.md §9 threat table are all false against committed code: `version_check.py`:59-66 makes a direct urllib.request call to `https://api.github.com/repos/.../releases/latest` on the first status/hint of every session, default-enabled (config-defaults.yaml `version_check.enabled`: true, hardcoded fallback in status.py) and silent on failure; sprint.py:1397 runs `git fetch origin` in the plan preflight (--no-fetch exists to skip it). Neither path goes through gh nor a Verify line; the version-check feature appears nowhere in the PRD's feature inventory or Section 8 integration map (gh CLI only). Both features were deliberate, consented designs (CR0044; the fetch preflight) - the defect is that the security-facing contracts were never amended, so a security reviewer or rebuilder would miss a default-on outbound call entirely (LL0013). Six panel votes, all not-refuted.

## Impact

prd.md:370 ('No network calls except gh and the tools a project's Verify lines invoke'), trd.md rule 6 (lines 245-246, 'No network access except the gh CLI wrapper in `github_sync.py`') and the trd.md §9 threat table are all false against committed code: `version_check.py`:59-66 makes a direct urllib.request call to `https://api.github.com/repos/.../releases/latest` on the first status/hint of every session, default-enabled (config-defaults.yaml `version_check.enabled`: true, hardcoded fallback in status.py) and silent on failure; sprint.py:1397 runs `git fetch origin` in the plan preflight (--no-fetch exists to skip it).

## Acceptance Criteria

- [ ] PRD Security NFR and Section 8 integration map enumerate the version check (direct HTTPS to api.github.com, default-on, `version_check.enabled` opt-out, silent-failure semantics) and sprint plan's git fetch origin
- [ ] The version check appears in the PRD feature inventory
- [ ] trd.md rule 6 and the §9 threat/controls rows name all three network paths (gh wrapper, version check urllib, git fetch) with their trust boundaries

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Raised |
