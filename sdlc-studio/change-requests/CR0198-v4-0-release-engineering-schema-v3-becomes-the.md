# CR-0198: v4.0 release engineering: schema v3 becomes the default, upgrade walk, major-release checklist

> **Status:** Complete
> **Created:** 2026-07-08
> **Created-by:** sdlc-studio new
> **Priority:** High
> **Type:** process

## Summary

Every schema-v3 capability ships dormant behind `schema_version: 3` (defaults to 2), and
the stated v4.0 rule is "cut only once the backlog is complete AND it has been tested in
anger on real projects" - but no artifact tracks the release act itself. The default
flip is the breaking change of v4; leaving it untracked means rc1 scope lives in heads,
not files.

This CR is the v4.0 release-engineering unit:

- **Flip the default**: `schema_version` defaults to 3 for NEW projects (`init`);
  existing v2 projects are never auto-flipped - they upgrade explicitly via
  `migrate_v3.py` with the documented walk. The era-gating that protects v2 projects
  stays.
- **The v3 -> v4 upgrade walk**: `project upgrade` on a v2 project presents the
  migration as a directed sequence (capability delta, migrate_v3 dry-run, apply,
  re-baseline per CR0197), rehearsed end-to-end on at least two real consuming projects
  before rc1 - that rehearsal IS the "tested in anger" gate, with findings filed as
  bugs/CRs.
- **Major-release checklist**: extend `templates/workflows/release-gate.md` with a
  majors-only section - breaking-change inventory named in CHANGELOG, migration
  rehearsal evidence linked, eval scenarios re-run, README/docs saying v4 in the right
  places, rc tag (`v4.0.0-rc.1`) cut from a green gate with the soak window before
  `v4.0.0`.
- **Version/doc sweep**: CHANGELOG [Unreleased] converts to the 4.0.0 sections;
  `check_versions.py` homes at 4.0.0-rc.1; the dormant-schema-v3 warning banners in
  CHANGELOG/LATEST/README come out (they describe the pre-v4 state).

Out of scope: EP0014 (its own epic), CR0194/CR0195 (new gates - separate operator call
on whether they ride 4.0 or 4.1), the debt CRs (non-breaking, any 4.x).

## Acceptance Criteria

- [ ] `init` scaffolds `schema_version: 3`; a fixture v2 project is untouched by the
      flip (era-gate regression test)
- [ ] `migrate_v3.py` + `project upgrade` walk rehearsed on two real consuming projects;
      findings filed; rehearsal evidence linked from the release notes
- [ ] `templates/workflows/release-gate.md` gains the majors-only checklist section
- [ ] Version strings, CHANGELOG conversion and banner removals land in one commit
      gated on lint + tests + gate
- [ ] rc tag checklist: `v4.0.0-rc.1` requirements enumerated (green gate, rehearsal
      done, EP0014 closed, open-bug count 0) so the tag decision is a checklist read,
      not a judgement call

## Evidence

- Operator direction 2026-07-08: v4 is the maturity release; rc1 must not ship with
  half the backlog incomplete; push withheld until rc-ready.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-08 | sdlc | Created via `new` (deterministic) |
| 2026-07-08 | claude | Filed at v4 readiness review |
