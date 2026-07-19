# CR-0285: PRD Section 9 configuration reference is wrong on four counts: gate defaults inverted, a retired env var documented as live, four live env vars omitted, and two_backlog.enforce undocumented everywhere

> **Status:** Complete
> **Decomposed-into:** EP0071
> **Priority:** High
> **Type:** docs
> **Size:** M
> **Affects:** sdlc-studio/prd.md, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

Four verified falsehoods in one section. (1) The table declares `require_ac_verification` defaults 'on'; the shipped default is false with the opposite adopt-incrementally philosophy (config-defaults.yaml:71, reference-outputs.md:716), and the actually hard-by-default Done gate (`quality.done_requires_verified`, transition.py:408-415) is absent from the table. (2) The preamble's universal claim 'the default is ON... an absent config blocks rather than disarms' is contradicted by the shipped G1/G2 two-backlog gates (`sdlc_md.py`:674, default False by deliberate EP0034 design), and the key appears in neither the PRD, config-defaults.yaml, nor reference-config.md. (3) `SDLC_ENGAGEMENT_STRICT` is documented as a live warn-by-default opt-in; the hook blocks unconditionally and the var is inert (`test_commit_msg_hook.py` asserts no value changes it, BG0134). (4) The env-var table omits every variable the scripts actually read: `SDLC_AUTHOR` (feeds the author!=reviewer independence gate), `SDLC_VERIFY_HTTP_HOSTS` (the SSRF allowlist, also missing from the Security section), `SDLC_TRIAGE_SESSION`, `SDLC_DEBUG.` All ten panel votes across the four source findings were not-refuted except one arguing partial coverage elsewhere; one table rewrite fixes the lot.

## Impact

Four verified falsehoods in one section.

## Acceptance Criteria

- [ ] `require_ac_verification` documented default false with the incremental-adoption note; `quality.done_requires_verified` added as the hard-by-default Done gate
- [ ] The 'default is ON / absent blocks' preamble restated with the deliberate `two_backlog.enforce` default-off exception; the key documented in the PRD table, config-defaults.yaml and reference-config.md
- [ ] `SDLC_ENGAGEMENT_STRICT` row removed or marked retired (blocking is unconditional; --no-verify is the one escape)
- [ ] `SDLC_AUTHOR`, `SDLC_VERIFY_HTTP_HOSTS`, `SDLC_TRIAGE_SESSION` and `SDLC_DEBUG` added to the env-var table; `SDLC_VERIFY_HTTP_HOSTS` also named in the Security NFR

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Raised |
