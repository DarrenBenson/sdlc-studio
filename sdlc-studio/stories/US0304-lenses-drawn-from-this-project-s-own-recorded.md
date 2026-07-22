# US0304: Lenses drawn from this project's own recorded failure modes

> **Status:** Review
> **Delivers:** CR0382
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/templates/audit-profiles/test.md,.claude/skills/sdlc-studio/scripts/tests/test_audit_profiles.py
> **Epic:** EP0101
> **Points:** 3

## User Story

**As a** finder agent handed the `test` lens profile
**I want** each lens to name the recorded failure mode it was drawn from
**So that** the run hunts classes this project has already paid review rounds for,
instead of a generic list re-derived from first principles

## Context

CR0382 is explicit that the lenses come from failure modes this project has actually
produced, not from a taxonomy. The four the request names map onto recorded lessons:

- **can-it-fail** - a guard every caller short-circuits, so nothing pins it; a test that
  passes whether or not the property holds.
- **reaches-the-code** - a test that looks behavioural but never enters the branch it
  names.
- **docstring-vs-assertion** - a docstring or comment asserting a bound the code does
  not provide, or describing an assertion the test does not make.
- **incidentally-green** - green for a reason unrelated to the property under test.

US0303 delivers the pack as a surface. This story is the content, plus the check that
the content stays anchored: a lens added later without a cited failure mode is a lens
invented from first principles, and the pack is where that would go unnoticed.

The pack ships with the skill, so citations must resolve in the shipped registry
(`lessons/_index.md`, `LL####`). The project-local log (`.local/lessons.md`, `L-####`)
is not shipped and its ids do not exist in a consuming project.

## Acceptance Criteria

### AC1: the four lenses the request names are declared, each with a question and a hunt list

- **Given** the `test` pack's lens table
- **When** it is parsed by `audit.py`'s pack parser
- **Then** it yields the four lenses named above, each with a non-empty adversarial
  question and a non-empty "hunts for" cell, so no row degrades into a bare heading
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_audit_profiles.py::TestProfileLensTests::test_the_four_lenses_are_declared_with_question_and_hunts
- **Verified:** yes (2026-07-22)

### AC2: every lens cites a recorded failure mode, and every citation resolves

- **Given** the shipped lessons registry at `lessons/_index.md`
- **When** the pack is read
- **Then** every lens row carries at least one `LL####` id, and every id cited resolves
  to an entry in that registry, so a lens with no recorded failure behind it cannot be
  appended silently and a lesson id cannot rot into a dangling reference
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_audit_profiles.py::TestProfileLensTests::test_every_lens_cites_a_lesson_id_that_resolves
- **Verified:** yes (2026-07-22)

### AC3: the lens set is calibrated against the review that motivated it

- **Given** the prose MAJORs recorded from RUN-01KY1WCR - among them a comment reading
  "same answer as before" on a narrowed `except` clause that had in fact made a shipped
  library path raise, and a hook comment reading "the expensive lanes ran either way"
  when they had not
- **When** the `test` profile is run over this repo's own suite and source
- **Then** at least one of them is reproduced as a candidate that survives the refute
  panel, and which one is recorded, proving the lens set is not vacuous
- **Verify:** manual run `audit run --profile test` over this repo and record which
  recorded MAJOR the run reproduced. Deliberately not executable: a lens run is an agent
  fan-out with a refute panel, not a subprocess with an exit code, and shelling it out
  would time out into a false `failed`.

## Resolved Questions

- **The calibration corpus is the two MAJORs the CR names concretely** (D0053). CR0382
  contradicts itself - its Impact section names two prose MAJORs from RUN-01KY1WCR, its
  acceptance criterion says three. AC3 stands as written against the two, because a
  calibration corpus must be enumerable and the third is not identifiable. The
  discrepancy is recorded rather than settled by taking the larger number: inflating a
  corpus to match a criterion is how an unfalsifiable claim gets written down.
- **Citations are shipped `LL####` ids only.** The pack ships to consuming projects where
  a project-local `L-####` id resolves to nothing, so a local id would be a dangling
  reference the moment the pack left this repo. The lenses' seeds were recorded locally
  first; each cites the shipped registry entries that carry the same failure class.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-22 | sdlc-studio | Built: four lenses with cited lesson ids; corpus and citation rulings recorded (D0053); AC1/AC2 verified, AC3 manual |
