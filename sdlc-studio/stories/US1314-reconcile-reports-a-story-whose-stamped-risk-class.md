# US1314: Reconcile reports a story whose stamped risk class is below the class its Affects now get from the map, and apply raises it

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0739
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/reference-reconcile.md, .claude/skills/sdlc-studio/scripts/tests/test_reconcile_risk_class.py, changelog.d/US1314.md
> **Epic:** EP0376
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** Reconcile reports a story whose stamped risk class is below the class its Affects now get from the map, and apply raises it
**So that** CR0739 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Reconcile reports a stamped class below what the map now gives

- **Given** a project whose map makes `src/pay` high, and an open story stamped `standard` whose Affects names `src/pay/charge.py`
- **When** `reconcile.py detect` is run
- **Then** it reports a risk-class drift item naming the story, its stamped class and the class the map gives. Fails on: the stamp read as authoritative and nothing reported, or a story with no map declared reported
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile_risk_class.py::RiskClassDriftTests::test_a_stamp_below_the_map_is_reported

### AC2: Apply raises the stamp and never lowers one

- **Given** that story, a second open story stamped `high` whose Affects the map classes standard, and a Done story stamped `standard` on a high path
- **When** `reconcile.py apply` is run
- **Then** the first story's stamp becomes high, the second keeps high, the Done story is untouched, and a second apply changes nothing. Fails on: a stamp lowered (an operator's raise undone), a closed unit rewritten, or apply not idempotent
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile_risk_class.py::RiskClassDriftTests::test_apply_raises_open_stamps_and_never_lowers_one

### AC3: The drift kind is documented

- **Given** `reference-reconcile.md`
- **When** it is read
- **Then** it names the risk-class drift kind, that apply only raises, and why. Fails on: an undocumented drift kind
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile_risk_class.py::RiskClassDriftTests::test_the_reference_names_the_risk_class_kind

## Notes

- A stamped class wins over the map (`critic.unit_risk_class`), so a map declared after refine leaves every earlier story at its old class: the gap this closes for any project, found while delivering D0520.
- Add the kind to `DRIFT_KINDS`; follow an existing per-story field kind for detect and apply.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-17 | Claude Opus 5.5 (grooming) | Groomed: authored criteria with Verify lines and notes |
