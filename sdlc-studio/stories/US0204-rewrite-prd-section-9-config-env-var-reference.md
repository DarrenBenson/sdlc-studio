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

- **Given** {{context}}
- **When** {{action}}
- **Then** `require_ac_verification` documented default false with the incremental-adoption note; `quality.done_requires_verified` added as the hard-by-default Done gate
- **Verify:** {{executable check}}

### AC2: The 'default is ON / absent blocks' preamble restated with the deliberate `two_backlog.enforce`

- **Given** {{context}}
- **When** {{action}}
- **Then** The 'default is ON / absent blocks' preamble restated with the deliberate `two_backlog.enforce` default-off exception; the key documented in the PRD table, config-defaults.yaml and reference-config.md
- **Verify:** {{executable check}}

### AC3: `SDLC_ENGAGEMENT_STRICT` row removed or marked retired (blocking is unconditional; --no-verify is

- **Given** {{context}}
- **When** {{action}}
- **Then** `SDLC_ENGAGEMENT_STRICT` row removed or marked retired (blocking is unconditional; --no-verify is the one escape)
- **Verify:** {{executable check}}

### AC4: `SDLC_AUTHOR`, `SDLC_VERIFY_HTTP_HOSTS`, `SDLC_TRIAGE_SESSION` and `SDLC_DEBUG` added to the

- **Given** {{context}}
- **When** {{action}}
- **Then** `SDLC_AUTHOR`, `SDLC_VERIFY_HTTP_HOSTS`, `SDLC_TRIAGE_SESSION` and `SDLC_DEBUG` added to the env-var table; `SDLC_VERIFY_HTTP_HOSTS` also named in the Security NFR
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
