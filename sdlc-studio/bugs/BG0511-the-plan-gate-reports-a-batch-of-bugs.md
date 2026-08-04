# BG0511: the plan gate reports a batch of bugs groomed when the transition gate refuses them outright

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_points.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_rolling.py, .claude/skills/sdlc-studio/scripts/tests/test_bug_regressions.py, .claude/skills/sdlc-studio/scripts/tests/test_autosprint.py, .claude/skills/sdlc-studio/scripts/tests/test_points_model.py
> **Evidence:** Reproduced by the author against the live tree: breakdown over the 17-unit run-1 worklist printed `breakdown: 17 unit(s), 0 ungroomed`, while `transition.py set --status Fixed --dry-run` refused BG0488, BG0491, BG0493, BG0495 and BG0497 for having no acceptance criteria. Independently found by the engineering and QA seats at the goal review.
> **Created:** 2026-08-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch
> **Verification depth:** functional

## Summary

`sprint.py breakdown` and `sprint.py plan --write` compute their ungroomed census over STORIES only. A bug with no `## Acceptance Criteria` section at all, or one carrying only `refine`-minted placeholder text, passes the plan gate silently. A 17-unit batch containing five bugs with no criteria section was reported as `0 ungroomed` and was plannable; the same five are refused by `transition.py set --status Fixed` with `no acceptance criteria; Fixed requires at least one`. So the planner admits work the deliverer cannot terminate, and the operator learns this at delivery rather than at planning - which is the whole reason the ungroomed census exists. Found at the plan-time goal review for the run-1 batch, by two independent seats, each by reading the bugs rather than trusting the census. It is adjacent to BG0491 (lane-check scans only stories) but is a separate gate on a separate command: BG0491 is about the duplicate-verifier number, this is about whether a batch is plannable at all.

## Steps to Reproduce

1. Build a worklist naming BG0488, BG0491, BG0493, BG0495 and BG0497.
2. Run `sprint.py breakdown --worklist <file>` - it reports `0 ungroomed`.
3. Run `transition.py set --id BG0493 --status Fixed --dry-run` - it refuses with `no acceptance criteria; Fixed requires at least one`.
4. The same unit is simultaneously plannable and unterminable.

## Proposed Fix

Extend the ungroomed census to every unit type the batch can contain, not stories alone. Two shapes must both count: an absent Acceptance Criteria section, and a section whose every criterion is a `refine` placeholder - `conformance.story_is_ungroomed` already knows the second shape and is only ever asked about stories. Then pin the census with a bug fixture, so the check cannot regress to story-only again.

## Acceptance Criteria

- [x] **AC1: a unit of any type with no acceptance criteria at all is reported ungroomed and refuses the plan.**
  - **Given** a batch containing a bug with no `## Acceptance Criteria` section - the state
    `transition.py set --status Fixed` already refuses
  - **When** `sprint.py breakdown` and `sprint.py plan --write` run over it
  - **Then** the bug is named in the ungroomed census and the plan is refused, so the planner and
    the deliverer answer the same question the same way instead of one admitting what the other
    rejects
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::UngroomedCensusCoversEveryTypeTests::test_a_bug_with_no_criteria_is_ungroomed
  - **Verified:** yes (2026-08-04)

- [x] **AC2: criteria that are entirely tool-derived are not authored criteria.**
  - **Given** a bug whose every criterion is one `file_finding` derived from its own prose - the
    `_CRITERION_FORM` shapes it writes when a finding is filed
  - **When** the census runs
  - **Then** the unit is reported ungroomed, naming that its criteria are derived rather than
    authored, because a criterion restating the summary cannot be judged pass or fail and two
    review seats had to read the bugs by hand to discover it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::UngroomedCensusCoversEveryTypeTests::test_all_derived_criteria_are_not_authored
  - **Verified:** yes (2026-08-04)

- [x] **AC3: the answer has one definition, and an authored bug is not a false positive.**
  - **Given** a bug carrying authored criteria with `Verify:` lines, and the derived-criterion
    shapes read from `file_finding`'s own table rather than a second copy of the strings
  - **When** the census runs over it
  - **Then** it is reported groomed, and the predicate the census consults is the same one
    `transition` consults, so the two cannot drift into disagreeing on identical bytes
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::UngroomedCensusCoversEveryTypeTests::test_an_authored_bug_is_not_reported_and_the_predicate_is_shared
  - **Verified:** yes (2026-08-04)

## Verification evidence

Functional. Four mutants executed, `__pycache__` purged before each and the child run under
`python3 -B`, each anchor asserted unique before patching and the source verified byte-identical
after:

| Mutant | Result |
| --- | --- |
| restore the `type == "story"` restriction in the census | killed |
| drop the `no-criteria` leg of `unit_is_ungroomed` | killed |
| drop the `derived-only` leg | killed |
| blind `_derived_openings` by returning `()` | killed |

Driven on the real backlog, not only fixtures: `sprint breakdown --stories Ready --bugs Open`
reported `0 ungroomed` before and **16 of 48** after, naming each unit and which of the three
shapes it is in. Full suite green: `run-suite.sh all` exit 0, `Ran 5896 tests ... OK (skipped=6)`. `npm test` separately exits 1 on the pre-existing test-noise budget (124 diagnostic lines against a baseline of 120), identical at the base ref and not this diff.

**One defect found in this repair, by running it.** The first draft wrapped the `derived-only`
leg in a bare `except Exception: pass`, and the import inside it was wrong (`import sdlc_md`
where the module is `lib.sdlc_md`). The leg was inert while four of the five new tests passed -
the same shape this unit exists to catch, in the unit that catches it. The except is gone: an
unimportable writer is a broken install, not a groomed batch.

**A shipped invariant was narrowed deliberately.** `test_the_round_trip_filed_then_plannable`
pinned "filed, therefore plannable", and that is precisely what admitted the sixteen. The
contract is now split at the line where the knowledge is: the FOOTPRINT (`Affects`, `Points`)
is known at filing and refused at filing; CRITERIA are authored at grooming and refused at
planning. Both halves are pinned, the second by a new test so the narrowing cannot quietly
revert. 22 test fixtures across 8 modules claimed `groomed=True` while writing no criteria at
all; they were asserting something untrue and now write a criterion.

## Round 2: what the independent review rejected, and what changed

REJECTed with one blocking finding, reproduced in an isolated worktree.

**The census refused types the deliverer never asks about.** `transition` demands criteria only
where `sdlc_md.executes_verifiers` holds - story and bug. The first draft applied `_has_criteria`
to every type with no guard, so on this tree 57 of 57 RFCs and 114 of 207 epics became ungroomed,
and the refusal message said a terminal status would refuse them when `transition.py set --id
CR0001 --status Complete --dry-run` in fact succeeds. That is the same drift AC3 forbids, running
the other way: the planner refusing what the deliverer admits. The leg is now scoped by
`executes_verifiers`, and a test pins both polarities - `cr`, `rfc` and `epic` unrefused, `story`
and `bug` refused - so neither direction can return silently.

Also repaired from the non-blocking set, all three being claims of mine the reviewer falsified:

- `_CRITERION_FALLBACK` matched by its PREFIX degenerated to the two words "The recorded", so an
  authored criterion opening with them read as tool-derived. Matching is now against the whole
  form, built from the form itself, which also fixes the docstring's overclaim about a form whose
  placeholder comes first.
- The comment claimed the creation-time filter was "gated on the reason CODE rather than its
  prose". Only the DECISION to filter is; which gaps are dropped is still a prose match on a
  message `sprint` owns. The coupling is now stated, with the reason it is tolerable - rewording
  breaks 44 tests loudly rather than silently.
- Two docstrings asserted the pre-narrowing contract the diff had just replaced: `check_groomed`
  still claimed neither creator "can mint a unit the other end of the pipeline rejects", and
  `grooming_gaps` still called its result the unmodified breakdown verdict.

The declared `Affects` was wrong in both directions and is corrected: `file_finding.py` carried a
production contract change and was undeclared, while `tests/test_conformance.py` was declared and
untouched.

Confirmed unweakened by the reviewer's own probes: no fixture that deliberately tested a refusal
now passes vacuously, and the three narrowed invariants still fail on a real footprint regression.

## Impact

A batch is admitted to a run that cannot reach terminal, so the run's first honest signal is a refusal at delivery. In the batch that exposed this, 21 of 58 points were unterminable and a further 12 carried placeholder criteria - over half the run, invisible to the command whose job is to say whether the backlog is worth planning from.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-03 | sdlc-studio | Filed |
