# US0623: a finding closed by FILING is recorded distinctly from one closed by fixing

> **Status:** Review
> **Delivers:** CR0506
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Epic:** EP0205
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** the next agent inheriting a run's residue
**I want** a finding closed by filing a bug recorded as filed, with the artefact id
**So that** "we fixed it" and "we wrote it down and moved on" cannot be read as the same outcome

## Notes

Delivers criterion 4 of CR0506. Both dispositions are legitimate under the operator's rule - a
non-stop-ship finding becomes a bug and the story closes - so this is not a gate. What is not
legitimate is being unable to tell them apart afterwards.

The distinction is what makes `EP0206`'s rule safe to enforce. If closing a story by filing is
indistinguishable from fixing it, "a sprint ends with nothing open" is satisfiable by filing
everything, and the record loses the difference between a batch that was repaired and one that
was deferred wholesale.

The filed id must resolve. An id naming no artefact is the same failure as a `Verify:` line
naming a test that does not exist - a reference nobody follows until the day it matters.

## Acceptance Criteria

### AC1: a filed closure records the disposition and the artefact id

- **Given** a finding closed by filing it as a bug
- **When** the repair is recorded
- **Then** the closure carries the disposition FILED and the artefact id, distinct from a closure
  carrying evidence of a fix, and both appear in the record rather than one being inferred from
  the other's absence
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::FiledDispositionTests::test_a_filed_closure_records_the_disposition_and_the_id
- **Verified:** yes (2026-08-03)

### AC2: a filed closure naming an unresolvable id is refused

- **Given** a closure declaring FILED against an id that resolves to no artefact
- **When** it is recorded
- **Then** it is refused, naming the id - a reference nobody can follow records the appearance of
  a disposition rather than one
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::FiledDispositionTests::test_a_filed_closure_with_an_unresolvable_id_is_refused
- **Verified:** yes (2026-08-03)

### AC3: the two dispositions are counted separately where the residue is read

- **Given** a repair mixing fixed and filed closures
- **When** the record is reported
- **Then** the counts are stated separately, so a reader sees how much of a rejection was
  repaired and how much was deferred - a single "closed" total is the shape that makes deferral
  invisible
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::FiledDispositionTests::test_fixed_and_filed_are_counted_separately
- **Verified:** yes (2026-08-03)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-03 | Claude Opus 5 | Groomed against CR0506 criterion 4, with the unresolvable-id refusal made a criterion after the same failure shape in Verify lines |
