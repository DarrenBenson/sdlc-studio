# CR-0044: skill version check + consent `skill-update`

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Feature
> **Requester:** Darren Benson
> **Date:** 2026-06-21
> **Affects:** scripts/version_check.py (new), reference-skill-update.md (new), help/skill-update.md (new), scripts/status.py, SKILL.md, templates/config-defaults.yaml, AGENTS.md, templates/agent-instructions.md, install.sh
> **Depends on:** --
> **GitHub Issue:** --

## Summary

The skill should tell a user when a newer SDLC Studio release exists and offer to
update the install, without nagging. A deterministic `version_check.py` compares the
installed version to the latest published GitHub release and, on the first
`status`/`hint` of a session, surfaces a one-line "update available" notice; a new
`skill-update` action upgrades the install (scope-detected) on explicit confirm.
Design forks were settled in discussion (2026-06-21) - this is a scoped, agreed feature.

## Settled design decisions

- **Startup mechanism: on first use.** Agent Skills have no native startup hook, so the
  check runs on the first `status`/`hint` invocation of a session (the existing
  version-check point) + an `AGENTS.md` "on session start" instruction. Portable across
  all five tools; no `settings.json` edits, no Claude-Code-only hook.
- **Latest = the newest GitHub *release tag*** (releases API, public, no auth), not
  `main` - users are notified only about published releases.
- **Network on by default, opt-out.** `version_check.enabled: false` in `.config.yaml`
  disables it; any network failure / rate-limit degrades silently (never errors, never
  blocks); a ~24h TTL cache means at most one ping per day.
- **`skill-update` runs the installer on explicit confirm** - distinct from the existing
  `upgrade` (project schema migration). It detects scope from the running script's path
  (user `~/.claude/...` / project `.claude/...` / `.agents/...`), shows the change, and
  on `y` runs `install.sh` for that target (which already sweeps every tool's copy),
  then says to reload. No silent mid-session overwrite; no default auto-update.
- **No nagging = per-version snooze.** Declining records the latest version in the
  install's `.local/version-check.json`; the notice stays quiet until a release *newer
  than the dismissed one* appears. Per-install (user vs project track their own).

## Proposed Changes

| Item | Detail |
| --- | --- |
| `scripts/version_check.py` (new) | `check` -> {installed, latest, status: up-to-date / update-available / snoozed / offline / disabled}; reads the installed `SKILL.md` version, fetches the latest release tag (TTL-cached in `.local/version-check.json`), compares semver, respects the snooze + the `enabled` config; `snooze` records the latest as dismissed; `scope` reports the detected install scope. Pure stdlib; network via a guarded `curl`/urllib, silent on failure. |
| `scripts/status.py` wiring | `status`/`hint` call `version_check check` and print the one-line notice only when `update-available`; nothing otherwise. |
| `skill-update` action | `reference-skill-update.md` + `help/skill-update.md`: scope-detect -> confirm -> run the installer for the target -> reload prompt; on decline, snooze. SKILL.md router + type-reference rows. |
| config | `version_check.enabled` (default true) + `version_check.ttl_hours` (default 24) in `config-defaults.yaml`. |
| instructions | An "on session start, surface any available update" line in `AGENTS.md` + `templates/agent-instructions.md`. |

## Impact Assessment

| Module | Impact | Change Type |
| --- | --- | --- |
| scripts/version_check.py | the deterministic check + snooze + scope | New |
| scripts/status.py | surface the notice on status/hint | Modified |
| reference-skill-update.md / help/skill-update.md | the consent update workflow | New |
| SKILL.md, config-defaults.yaml, AGENTS.md, agent-instructions.md | wiring + config + instruction | Modified |

### Breaking Changes

None. Additive; on-by-default but fully opt-out, silent offline, no artifact-schema
change. `skill-update` is a new action; the existing `upgrade` (schema) is untouched.

## Acceptance Criteria

- [ ] `version_check check` compares the installed `SKILL.md` version to the latest GitHub release tag and returns a status; on any network failure it returns `offline` silently (exit 0, no error output).
- [ ] Results are TTL-cached (default 24h) so repeat calls within the window do not refetch; a per-version snooze yields `snoozed` when the latest equals the dismissed version; `version_check.enabled: false` yields `disabled` and makes no network call.
- [ ] `status`/`hint` print a single "vX.Y.Z available - run `/sdlc-studio skill-update`" line only when `update-available`, and nothing when up-to-date / snoozed / offline / disabled.
- [ ] `skill-update` detects the install scope from the running script path and, on explicit confirm, runs `install.sh` for that target; declining records the snooze. Unit-tested (semver compare, TTL cache, snooze, scope detection, offline + disabled degradation).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Darren Benson | Raised - auto version check + consent self-update; design forks settled in discussion (release-tag source, network-on-by-default opt-out, run-on-confirm, `skill-update` name, per-version snooze, on-first-use) |
