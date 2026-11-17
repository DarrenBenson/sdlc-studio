# US1313: This repository's config declares the D0520 component map, and a test pins each gate script to high

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0739
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/.config.yaml, tools/tests/test_repo_risk_map.py, changelog.d/US1313.md
> **Epic:** EP0376
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** This repository's config declares the D0520 component map, and a test pins each gate script to high
**So that** CR0739 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The gate scripts are high, the other scripts elevated, the rest standard

- **Given** this repository's `sdlc-studio/.config.yaml`
- **When** `lib/risk_class.load_map` reads it and classifies `scripts/gate.py`, `scripts/critic.py`, `scripts/transition.py`, `scripts/sprint.py`, `scripts/verify_ac.py`, `.githooks/pre-push`, `scripts/refine.py` and `docs/evidence.md`
- **Then** the first six are high, `refine.py` is elevated and the page is standard, and the map loads with no notes. Fails on: a gate script classed below high, a misspelt class kept as standard with a note, or a prefix that matches a sibling path
- **Verify:** pytest tools/tests/test_repo_risk_map.py::RepoRiskMapTests::test_the_gate_scripts_are_high_and_the_other_scripts_elevated

### AC2: A bug that changes a gate reads as high in review

- **Given** an open bug whose Affects names `scripts/critic.py`
- **When** `critic.unit_risk_class` reads it in this repository
- **Then** it returns high. Fails on: a bug touching a gate still read as standard
- **Verify:** pytest tools/tests/test_repo_risk_map.py::RepoRiskMapTests::test_a_bug_touching_a_gate_reads_high

## Notes

- D0520. Deliver in run sixteen's last wave, so the run's own reviews are held to one policy from plan to close.
- Mapped paths are prefixes under `.claude/skills/sdlc-studio/scripts/`; check the matcher's whole-segment rule against `sprint.py` versus `sprint_report.py` (the latter is elevated, not high).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-17 | Claude Opus 5.5 (grooming) | Groomed: authored criteria with Verify lines and notes |
