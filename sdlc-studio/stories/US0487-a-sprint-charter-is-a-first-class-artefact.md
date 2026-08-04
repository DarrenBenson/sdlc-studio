# US0487: A sprint charter is a first-class artefact: goal, scope rule and appetite, with a tool-allocated id and an index row

> **Status:** Ready
> **Delivers:** RFC0057
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
> **Epic:** EP0176
> **Points:** 5

## User Story

**As a** maintainer building the queue on the same footing as every other artefact
**I want** a sprint charter to be a real artefact carrying its goal, scope rule and appetite
**So that** a charter a second person must judge has an id, a history and an index row rather than being a line in a file

## Acceptance Criteria

### AC1: a charter is created with a tool-allocated id and an index row

- **Given** a workspace with a sprints directory and its index
- **When** a charter is created carrying a goal, a scope rule and an appetite
- **Then** it is written with an allocated id, its index row is appended, and no id is ever hand-authored
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::SprintCharterTests::test_the_charter_reaches_the_SHIPPED_ENTRY_POINT_not_only_the_library
- **Verified:** yes (2026-08-04)

### AC2: a charter missing the parts a run needs is refused at creation

- **Given** a charter request with no goal, or no scope rule
- **When** creation runs
- **Then** it is refused naming what is absent, because a charter nobody can materialise is not a charter
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::SprintCharterTests::test_a_charter_without_a_goal_or_scope_is_refused
- **Verified:** yes (2026-08-04)

### AC3: the charter's status vocabulary is derived, not restated at the call site

- **Given** the shared status vocabulary
- **When** a charter moves between states
- **Then** the permitted states come from the shared vocabulary rather than a set written beside the charter code, so the two cannot disagree about what queued or spent means
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::SprintCharterTests::test_the_status_vocabulary_is_derived_from_the_shared_source
- **Verified:** yes (2026-08-04)

## Verification evidence

Functional, driven through the shipped CLI on the live tree as well as in fixtures:
`artifact.py new --type charter` minted `SC0001` with `indexed=True`, and the same command with
a missing scope rule refused with no id allocated and nothing written.

Three mutants executed, `__pycache__` purged and each child run under `python3 -B`, anchors
asserted unique, source restored byte-identical:

| Mutant | Result |
| --- | --- |
| drop `charter` from the creator's type registry | killed |
| drop the `check_charter` guard from the creation path | killed |
| change the shared status vocabulary out from under the creator | killed |

The third is the one AC3 exists for. The charter's create status, terminal status and prefix are
DERIVED from `lib.sdlc_md` - the same authority the validator, the transition gate and the
archiver already read - so `artifact.SPEC["charter"]` is asserted as identity against that source
rather than against a second list written in the test. A second list in the test is the same
defect as a second list in the code, one layer out.

Two things are deliberately NOT required at creation. A charter carries no acceptance criteria:
it delivers nothing itself and the units it materialises carry their own. And its appetite is
optional, resolving from the project's capacity at materialise time - the rule `sprint plan`
already follows - so an absent one is not a gap.

**A schema change, refused until it was declared.** Adding an artefact type touches the
versioned contract in `reference-schema.md`, and five guards caught the omission at once: the
prefix table, the directory table, the status-vocabulary table, the creator-shape pin, and the
scaffold sweep. The contract now documents `SC`, `sdlc-studio/charters/`, and the Queued/Spent
vocabulary with its terminal set. The id patterns learned `SC` too - `extract_record_id` did not
recognise it, so the validator called a correctly-named charter malformed.

**And the lane-check refused this unit for the same reason it refused US0467 last run**: all
three verifiers called `artifact.new` as a library, never `main()`, so the CLI verb, its
`--type` choice and its field whitelist were unexercised. Twice in two runs. AC1 now drives
`artifact.main` and asserts the appetite survives the whitelist, and that is pinned rather than
remembered.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed against the D0072 rulings |
