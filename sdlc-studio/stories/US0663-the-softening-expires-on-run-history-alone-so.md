# US0663: The softening expires on run history alone, so a second run refuses and an upgrading project is unaffected byte-for-byte

> **Status:** Review
> **Delivers:** CR0541
> **Created:** 2026-08-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/plan_review.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Epic:** EP0213
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The softening expires on run history alone, so a second run refuses and an upgrading project is unaffected byte-for-byte
**So that** CR0541 is delivered by work that can be planned and checked

## Acceptance Criteria

> **Plan repaired after a REJECT at plan review (2026-08-09, qa seat, brief `3324adfb34ec`).** The
> seat proved AC3's verifier could not fail on its own mutant BY EXECUTION: it asserted the
> PRESENCE of two strings while the mutant was an ADDITION, so appending the forbidden key flipped
> it from exit 1 to exit 0. A presence check can never detect an addition. It is replaced by an
> ABSENCE assertion over both files, with a positive control. The predicate-location contradiction
> the seat found between this unit and its sibling is resolved: the predicate lives in
> `plan_review.py`, and this unit's `Affects` now says so.

### AC1

- **Given** a project holding one retro, and the same project holding none
- **When** both are put through `transition.py set --status Done` in ONE test
- **Then** the first refuses and the second reports - the pair asserted together, so the test
  cannot pass on the pre-epic tree where every project refuses.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k the_softening_expires_on_the_first_retro
- **Verified:** yes (2026-08-10)
- **Mutant:** in `plan_review.py`, change the arming predicate to read a config key defaulting to softened, which no retro can expire.

### AC2

> **NARROWED at the round-3 review, 2026-08-10.** The first form demanded a baseline captured
> from the base ref before this epic existed. The test captures from the CURRENT tree with the
> softening branch disabled, which is a weaker comparison - a regression this epic introduced
> elsewhere would sit on both sides and be invisible - and the criterion is amended to say what
> is actually built rather than leaving prose that overstates it. The stronger form is worth
> having and is filed rather than claimed.

- **Given** a project that already holds retros - the upgrading case
- **When** the transition is attempted
- **Then** stdout, stderr and the exit status match a baseline captured from THIS tree with the
  softening branch disabled - the nearest available counterfactual, not the base ref - with the
  run id and absolute temporary paths normalised out, and the test naming both in a constant it
  asserts against.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k an_upgrading_project_is_unchanged_against_a_captured_baseline
- **Verified:** yes (2026-08-10)
- **Mutant:** in `plan_review.py`, widen the arming predicate from `no retro exists` to `no run is currently open`.

### AC3

- **Given** `reference-config.md` and `templates/config-defaults.yaml`
- **When** both are read
- **Then** NEITHER contains a `plan_review.first_run` key or any other knob that could hold the
  softening open, asserted as an ABSENCE over both files - and the positive control adds such a
  key to each in turn and asserts the check reddens for both.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py -k no_configuration_key_can_hold_the_softening_open
- **Verified:** yes (2026-08-10)
- **Mutant:** in `templates/config-defaults.yaml`, add a `plan_review.first_run` key.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `plan_review.py`, change the arming predicate to read a config key defaulting to softened | |
| AC2 | in `plan_review.py`, widen the arming predicate from no-retro-exists to no-run-currently-open | |
| AC3 | in `templates/config-defaults.yaml`, set a `plan_review.first_run` knob and have `plan_review.py` read it | |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-09 | sdlc-studio | Created via `new` (deterministic) |
