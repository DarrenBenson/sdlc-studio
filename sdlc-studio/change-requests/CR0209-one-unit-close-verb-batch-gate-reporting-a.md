# CR-0209: one unit-close verb + batch gate reporting + a metadata-stamp verb (agent ergonomics of the unit lifecycle)

> **Status:** Complete
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

Dogfooded during the RV0007 fix-pack sprint (RETRO0017): three ergonomics gaps each cost real agent round-trips per unit. (1) No deterministic verb sets a metadata line - recording 'Verification depth' meant hand-editing nine artefact bodies in a system whose doctrine is never hand-do what a tool wires. (2) transition/close gates refuse ONE unmet requirement per attempt (depth gate, then triage gate, then done - three round-trips per close on a v3 workspace); each refusal already knows the full requirement set. (3) The per-unit close ceremony (depth stamp -> transition -> critic record -> telemetry close) is four mechanically coupled invocations that agents perform in fixed sequence every unit.

## Acceptance Criteria

- [ ] A deterministic verb sets/updates a named metadata line on an artefact (e.g. transition annotate --id BG0001 --field 'Verification depth' --value 'functional (...)'), index-safe and vocabulary-checked where applicable
- [ ] A blocked transition lists EVERY unmet gate requirement in one refusal, not the first only; a unit test proves a close missing depth AND triage reports both
- [ ] A unit-close orchestrator (e.g. artifact close --depth ... --verdict ... --reviewer ... --author ...) performs stamp + transition + critic record + telemetry in one call, refusing atomically if any gate blocks
- [ ] help/ and reference-scripts document the new verbs; the sprint loop reference points at the orchestrator

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Raised |
