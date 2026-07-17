# CR-0304: TRD Migrations section claims schema migration is 'not by the script layer' while committed main ships a three-script migration surface the TRD itself lists elsewhere

> **Status:** In Progress
> **Decomposed-into:** EP0071
> **Priority:** Low
> **Type:** docs
> **Size:** S
> **Affects:** sdlc-studio/trd.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

trd.md §6 Migrations (398-404, marked [HIGH] confidence) says migration is handled by reference-upgrade.md 'not by the script layer'. Committed main (d2e8417, RFC0041, after the TRD's last edit) ships migrate.py - self-described as 'the ORCHESTRATOR... emits ONE report' - plus `project_upgrade.py` (--apply performs the safe set) and `migrate_v3.py` (stamps `schema_version` 3, renames files). The TRD contradicts itself: its own rule 5 lists `migrate_v3.py` as a bounded writer and ADR-008 cites '`migrate_v3` adopt'; reference-upgrade.md itself says it is 'Backed by scripts/`project_upgrade.py`'. Additionally the 'upgrade' type named here does not appear in SKILL.md's type table, while the shipped 'migrate' type does. Small stale-paragraph fix. Verified 3x.

## Impact

trd.md §6 Migrations (398-404, marked [HIGH] confidence) says migration is handled by reference-upgrade.md 'not by the script layer'.

## Acceptance Criteria

- [ ] §6 Migrations names the shipped script surface (migrate.py orchestrator, `project_upgrade.py` --apply safe set, `migrate_v3.py)` alongside reference-upgrade.md
- [ ] The upgrade-vs-migrate type naming is reconciled with SKILL.md's type table

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Raised |
