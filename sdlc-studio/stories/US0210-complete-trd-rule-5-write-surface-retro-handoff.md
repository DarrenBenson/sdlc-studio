# US0210: Complete TRD rule 5 write surface (retro/handoff/archive/persona_gen) or restate as non-exhaustive with a census pointer

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/trd.md
> **Epic:** EP0071
> **Points:** 2

## User Story

**As an** engineer auditing the write contract
**I want** rule 5 to name the remaining writers and declare itself non-exhaustive with a census pointer
**So that** ADR-009's persona_gen writer and the retro/handoff/archive writers no longer contradict §5

## Acceptance Criteria

### AC1: Rule 5's writer list includes retro.py, handoff.py, archive.py, `persona_gen.py` and decisions.py

- **Given** rule 5's writer list omitted retro.py, handoff.py, archive.py and persona_gen.py, though each writes via `atomic_write` (decisions.py was already listed)
- **When** each is added to the list with its tested boundary (retro artefact + VELOCITY row, handoff + index + worklist, archive sub-index, generated cards)
- **Then** Rule 5's writer list includes retro.py, handoff.py, archive.py, `persona_gen.py` and decisions.py, each with its tested boundary
- **Verify:** grep -E "retro.py. writes the batch retro artefact" sdlc-studio/trd.md

### AC2: Or the rule is restated as non-exhaustive with a pointer to the authoritative writer census, and

- **Given** rule 5 read as a closed list while ADR-009 named persona_gen.py as a writer it did not include
- **When** rule 5 declares itself non-exhaustive, points at `reference-scripts.md` as the authoritative catalogue, and ADR-009 cross-links persona_gen.py as a §5 rule 5 writer
- **Then** Or the rule is restated as non-exhaustive with a pointer to the authoritative writer census, and ADR-009's description no longer contradicts §5
- **Verify:** grep -E "authoritative catalogue of the script write surface" sdlc-studio/trd.md

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
