# US0204: Rewrite PRD section 9 config/env-var reference: require_ac_verification default, two_backlog.enforce, retire SDLC_ENGAGEMENT_STRICT, add missing env vars

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/prd.md, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md
> **Epic:** EP0071
> **Points:** 3

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: `require_ac_verification` documented default false with the incremental-adoption note

- **Given** the §9 feature-flag table listed `require_ac_verification` with default `on` and named no verified Done gate
- **When** its default is corrected to `false` with the incremental-adoption note and `quality.done_requires_verified` is added as the hard-by-default Done gate
- **Then** `require_ac_verification` documented default false with the incremental-adoption note; `quality.done_requires_verified` added as the hard-by-default Done gate
- **Verify:** grep "done_requires_verified" sdlc-studio/prd.md

### AC2: The 'default is ON / absent blocks' preamble restated with the deliberate `two_backlog.enforce`

- **Given** the 'default is ON / absent blocks' preamble stated the rule without its one exception, and `two_backlog.enforce` was undocumented in the PRD table, config-defaults.yaml and reference-config.md
- **When** the preamble is restated naming the deliberate `two_backlog.enforce` default-off exception and the key is added to all three references
- **Then** The 'default is ON / absent blocks' preamble restated with the deliberate `two_backlog.enforce` default-off exception; the key documented in the PRD table, config-defaults.yaml and reference-config.md
- **Verify:** grep "two_backlog" .claude/skills/sdlc-studio/templates/config-defaults.yaml

### AC3: `SDLC_ENGAGEMENT_STRICT` row removed or marked retired (blocking is unconditional; --no-verify is

- **Given** the env-var table carried `SDLC_ENGAGEMENT_STRICT` as a live warn/block toggle, though the code retired it (the commit-msg gate blocks unconditionally under `--strict`)
- **When** its row is removed and a note records it retired, with `git commit --no-verify` as the one escape
- **Then** `SDLC_ENGAGEMENT_STRICT` row removed or marked retired (blocking is unconditional; --no-verify is the one escape)
- **Verify:** grep "SDLC_ENGAGEMENT_STRICT. is retired" sdlc-studio/prd.md

### AC4: `SDLC_AUTHOR`, `SDLC_VERIFY_HTTP_HOSTS`, `SDLC_TRIAGE_SESSION` and `SDLC_DEBUG` added to the

- **Given** the env-var table documented only `CLAUDE_SKILL_DIR` and the checksum flag, omitting four env vars the scripts read
- **When** rows are added for `SDLC_AUTHOR`, `SDLC_VERIFY_HTTP_HOSTS`, `SDLC_TRIAGE_SESSION` and `SDLC_DEBUG` (the Security NFR already names `SDLC_VERIFY_HTTP_HOSTS`)
- **Then** `SDLC_AUTHOR`, `SDLC_VERIFY_HTTP_HOSTS`, `SDLC_TRIAGE_SESSION` and `SDLC_DEBUG` added to the env-var table; `SDLC_VERIFY_HTTP_HOSTS` also named in the Security NFR
- **Verify:** grep "SDLC_TRIAGE_SESSION" sdlc-studio/prd.md

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
