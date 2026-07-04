# CR-0157: project upgrade should surface the capability delta, not just file corrections

> **Status:** Proposed
> **Created:** 2026-07-04
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Improvement

## Summary

`project_upgrade.py` migrates a consuming project's *artefacts* well (config scaffold,
`.version` bump, amigo cards, reconcile) but tells the operator nothing about what the new
skill can now *do*. Field report from a real 2.5.0 -> 3.4.0 upgrade: the migration ran
clean, yet the single most valuable new capability in that range - the mutation gate - was
discovered only by accident, because `gate.py` happened to print a `[warn] mutation: not
run` lane afterwards. The version arithmetic and a per-version CHANGELOG both exist; nothing
joins them at upgrade time. `project upgrade` should emit a "what changed since your recorded
`skill_version`" capability summary so the operator adopts the new features deliberately,
not by stumbling on a warn lane.

## Problem

A long-lived project records `skill_version` in `sdlc-studio/.version`. On upgrade,
`project_upgrade.py --root .` correctly reports "BEHIND - project schema 2 / skill 2.5.0 vs
skill 3.4.0" and lists the file corrections it will apply. But:

1. **No capability delta.** The operator learns which *files* changed, never which
   *features* arrived across the 15 minor/patch versions in the gap (mutation gate,
   brownfield-runbook, file_finding, constitution, per-project status vocab, ...). The
   CHANGELOG carries exactly this, keyed by version (`## [3.4.0]`, `### Added`), but the
   upgrade never reads it.
2. **New capability lands silent.** A feature added in the version range that isn't a file
   the migrator rewrites (a new *gate lane*, a new *script verb*, a new *reference doc*) is
   invisible to the upgrade. The mutation gate is the concrete case: post-upgrade its lane
   reads "not run", which reads as benign, not as "a new integrity check you have never
   baselined".
3. **The value of upgrading is left implicit.** `skill-update` gets the tool; `project
   upgrade` migrates the artefacts; neither answers the operator's actual question - *what
   do I get, and what should I now do?* The friction is not the mechanics (those are good);
   it is that adopting the new capabilities is undirected manual archaeology.

This is upgrade friction, not a mechanics bug - the deterministic set applied perfectly. It
is the difference between a migration that *completes* and one that also *onboards*.

---

## Proposed Changes

### Item 1: emit a "Changed since your version" capability summary in the upgrade report

**Priority:** Medium
**Effort:** S

`project_upgrade.py` reads the project's recorded `skill_version` and the installed skill
version (it already does, to compute BEHIND). Add a step that parses the root `CHANGELOG.md`
for the version entries strictly between the two and prints a compact, grouped digest under
a new **"Changed since <recorded>"** heading - `### Added` items first, then a one-line
pointer to any that introduce a new *gate lane*, *script verb*, or *reference doc* (the
capabilities a file-diff migrator can't surface). Dry-run shows it too. Degrade honestly: no
CHANGELOG, or an unparseable range, prints "capability delta unavailable (no parseable
CHANGELOG between X and Y)" rather than silence.

### Item 2: name the newly-available gate lanes an operator should baseline

**Priority:** Low
**Effort:** S

When a version in the gap introduced a `gate.py` lane that is *advisory-when-absent* (the
mutation lane is the archetype: "not run" reads as PASS-ish), the upgrade report names it
explicitly as an unbaselined new check - "3.4.0 added the mutation gate; it reports not-run
until you run `scripts/mutation.py` over your changed surface". One line per such lane,
sourced from a small declared registry so it stays honest as lanes are added. This is the
line that would have turned an accidental discovery into a directed next step.

---

## Impact Assessment

### Existing Functionality

Additive to the upgrade report only. No change to the deterministic correction set, its
idempotence, or its dry-run-by-default contract. A project with `skill_version` equal to the
installed version prints "already current" and no delta, as today.

### Affected Modules

| Module | Impact | Change Type |
| --- | --- | --- |
| `scripts/project_upgrade.py` | Adds a CHANGELOG-range parse + digest section to the report | Modified |
| `CHANGELOG.md` | Becomes a consumed artefact (must stay Keep-a-Changelog parseable per version) | Modified (contract) |
| `reference-upgrade.md` | Document the capability-delta section under `project upgrade` | Modified |
| gate-lane registry (new, small) | Declares which lanes are advisory-when-absent, for Item 2 | New |

### Breaking Changes

None. The CHANGELOG format is already the stated convention; this makes a parser depend on
it, so a malformed entry degrades to "unavailable", never a crash.

---

## Acceptance Criteria

- [ ] `project_upgrade.py` (dry-run and `--apply`) prints a "Changed since <recorded skill_version>" section digesting the CHANGELOG entries strictly between recorded and installed versions, grouped by change kind
- [ ] a capability that is not a migrated file (new gate lane / script verb / reference doc) still appears in the digest
- [ ] an advisory-when-absent gate lane introduced in the gap is named as an unbaselined new check with its one-line "run this to baseline" pointer (Item 2)
- [ ] honest degrade: absent or unparseable CHANGELOG prints an explicit "unavailable" line, never silence and never a crash; "already current" prints no delta
- [ ] unit tests pin the digest for a known version range and the degrade path; `reference-upgrade.md` documents the section; CHANGELOG `[Unreleased]`

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| CHANGELOG drifts from a machine-parseable shape | Medium | Low | Parser degrades to "unavailable"; a repo test can assert the CHANGELOG parses |
| Gate-lane registry rots as lanes are added | Low | Low | Small declared list co-located with the lanes; a test asserts every advisory-when-absent lane is registered |
| Digest too verbose over a large version gap | Low | Low | Group by kind, cap per-group with a "+N more, see CHANGELOG" tail |

---

## Dependencies

### CR Dependencies

| CR | Title | Status | Required Before |
| --- | --- | --- | --- |
| [CR-0152](CR0152-mutation-summary-states-its-sampling-coverage-explicitly.md) | Mutation summary states its sampling coverage explicitly | Proposed | Complementary, not blocking - CR-0152 fixes the mutation lane's *own* honesty; this CR makes the upgrade *point at* the lane. Same field report. |

### External Dependencies

| Dependency | Type | Status |
| --- | --- | --- |
| Root `CHANGELOG.md` remains Keep-a-Changelog per-version | Convention | Already in force |

---

## Out of Scope

- Changing the deterministic correction set or its safety contract (the mechanics are good).
- Auto-adopting the new capabilities (e.g. auto-running the mutation gate) - the upgrade
  *directs*, the operator *decides*. Consistent with dry-run-by-default.
- `skill-update` (tool upgrade) output; this CR is scoped to `project upgrade` (artefact
  migration), though the same digest could later be shared.

---

## Field Report (evidence)

Observed on the engram-framework repo, 2026-07-04, upgrading 2.5.0 -> 3.4.0:

- `project_upgrade.py --apply` ran clean: `.version` bumped, 3 amigo cards installed,
  reconcile 0 drift, gate PASS. Mechanics: no notes.
- The mutation gate (new in the range) was found only because `gate.py` printed
  `[warn] mutation: mutation gate not run`. Running it surfaced 25 real survivors on the
  integrity-critical surface (a default-budget sample had hidden 17 of them) - material
  coverage the operator would never have known to look for from the upgrade output alone.
- Net: the upgrade *completed* but did not *onboard*. Had it printed "3.4.0 added the
  mutation gate - not yet baselined; run `scripts/mutation.py`", the highest-value follow-up
  would have been a directed step, not an accident.

---

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | operator | CR proposed - field report from a live 2.5.0 -> 3.4.0 upgrade of a consuming project (engram-framework) |
