# BG0559: the doc-surface gate lane raises ModuleNotFoundError in every consuming project, so a new v5 lane reports NOT MEASURED forever on every user's gate run

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/command_audit.py, .claude/skills/sdlc-studio/scripts/doc_coverage.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py, .claude/skills/sdlc-studio/scripts/tests/test_doc_coverage.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** Probed through the shipped CLI on a throwaway consuming-project fixture, 2026-08-09, during a v5 release-readiness sweep. `gate.py --root <fixture>` prints `[warn] doc-surface [0.0s]: NOT MEASURED - command_audit.verb_coverage raised ModuleNotFoundError: No module named 'surface'`. `git log -S '_doc_surface' -- scripts/gate.py` returns only 4e0e4a0f (RUN-01KZF9AF, US0654), which is not an ancestor of v4.1.0, so the lane and its defect are both new in v5 and reach a consumer the moment v5 ships.
> **Created:** 2026-08-09
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_doc_surface` calls `command_audit.verb_coverage(root)`, which calls `_surface_module(skill)` and imports `lib/surface.py` from the skill tree it resolves under the project root. A consuming project has no skill tree there, the import raises, and the lane's blanket `except Exception` reports NOT MEASURED with count 1.

The count-1 choice is deliberate and correct in itself - US0654 reasoned that reporting 0 would render a broken measurement as perfect coverage. But it was reasoned for a lane that fails occasionally in the skill repo, not for a lane that fails unconditionally everywhere else. The result is that every consuming project's gate carries a permanent non-zero advisory naming an internal Python module the operator has no way to act on, and the surface that exists to be noticed becomes the surface everybody scrolls past.

The applicability check the lane needs already exists one lane above it. `_doc_coverage` returns `N/A (not the skill repo)` on the same fixture, in the same gate run, and `verb_coverage` is documented as measuring the SKILL's own hand-written corpus - a quantity that is undefined for a consuming project rather than merely unmeasurable there.

## Steps to Reproduce

1. Create any project that is not the skill repo: `init.py --root <dir> run` on a clean git repo is enough. 2. `python3 scripts/gate.py --root <dir>`. 3. Read the doc-surface line: `NOT MEASURED - command_audit.verb_coverage raised ModuleNotFoundError: No module named 'surface'`, count 1, on every run forever. 4. Compare with the doc-coverage line immediately above it, which correctly reports `N/A (not the skill repo)`.

## Proposed Fix

Give `_doc_surface` the same applicability test its sibling `_doc_coverage` already uses, and report `N/A (not the skill repo)` with count 0 when the project is not the skill repo. Keep the count-1 NOT MEASURED path for the case it was written for: an unexpected fault inside the skill repo, where the measurement IS defined and failing to take it is the finding. The two cases must stay distinguishable, because collapsing them is how a lane that is genuinely broken in the skill repo would start reading as somebody else's project. Pin both through `gate.py` itself on two fixtures - a skill-repo tree and a consuming-project tree - since the defect lives entirely in which tree the lane is pointed at and no in-process test of `verb_coverage` can see it.

## Acceptance Criteria

> **Plan repaired after a REJECT at plan review (2026-08-09, qa seat, brief `6d3f4214540b`).**
> Four blocking findings, and two changed what this unit is.
>
> **Ruling 1 - the predicate goes at the GATE, not inside `verb_coverage`.** The obvious repair
> is to make `verb_coverage` answer "not applicable" itself. The seat measured why that is wrong:
> `doc_coverage._skill_dir` returns None for a bare skill tree while `command_audit._skill_dir`
> returns it, and `command_audit.py --root .claude/skills/sdlc-studio --coverage` measures 257
> verbs there today. Pushing the test down would silently switch that CLI off, and no fixture
> shaped like a consuming project could see it. So the applicability question is asked where the
> LANE is, by the same predicate `doc-coverage` already answers it with.
>
> **Ruling 2 - the second reader is in scope, not deferred.** `sprint_report._ck_doc_surface`
> calls the identical measurement and returns `unreadable` on the same fixture, so a repair that
> satisfied only the gate would leave the identical permanent advisory in every consuming
> project's close report. `Affects` is widened rather than the gap recorded as an exclusion: it
> is one predicate and two callers, and splitting it would ship half a fix.

### AC1

- **Given** a project that is not the skill repo, built by `init run` in an empty tree
- **When** `gate.py --root <fixture>` is run AS A SUBPROCESS and its printed lane lines are read
- **Then** the `doc-surface` line reports the lane as not applicable with count 0, and the words
  `NOT MEASURED` and `ModuleNotFoundError` appear nowhere in it.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py -k doc_surface_is_not_applicable_outside_the_skill_repo
- **Verified:** yes (2026-08-09)
- **Mutant:** in `gate.py`, delete the applicability guard from `_doc_surface` so it calls the measurement unconditionally.

### AC2

- **Given** the skill repository itself
- **When** `gate.py --only doc-surface` is run AS A SUBPROCESS
- **Then** the lane still reports a real verb count, proving the lane was made inapplicable
  outside the skill repo rather than switched off everywhere, and
  `command_audit.py --root .claude/skills/sdlc-studio --coverage` still measures a bare skill
  tree - the CLI Ruling 1 exists to protect.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py -k doc_surface_still_measures_the_skill_repo_and_a_bare_tree
- **Verified:** yes (2026-08-09)
- **Mutant:** in `command_audit.py`, make `verb_coverage` consult the gate's applicability predicate itself, so a bare skill tree resolves to not-applicable.

### AC3

- **Given** a SKILL-SHAPED fixture - one the applicability predicate calls a skill repo - whose
  `scripts/lib/surface.py` is absent, so the measurement raises an import fault where the
  measurement IS defined
- **When** `gate.py --root <fixture> --only doc-surface` is run as a subprocess
- **Then** the lane reports `NOT MEASURED` with count 1, and the same fixture WITH the file
  present reports a real count - the positive control, without which a fixture broken for some
  unrelated reason passes for the wrong reason.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py -k an_import_fault_inside_a_skill_repo_still_reports_not_measured
- **Verified:** yes (2026-08-09)
- **Mutant:** in `gate.py`, narrow the `except Exception` on `_doc_surface` to `except ModuleNotFoundError` and return the not-applicable result from it, which is the careless repair this bug invites.

### AC4

- **Given** the two lanes `doc-coverage` and `doc-surface`, and the close report's
  `_ck_doc_surface`
- **When** the shared applicability predicate is replaced in-process
- **Then** all three follow, so the question has one reader rather than three answers.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py -k one_applicability_predicate_decides_for_every_reader
- **Verified:** yes (2026-08-09)
- **Mutant:** in `gate.py`, give `_doc_surface` a DIVERGENT inline copy that tests for the skill directory rather than for `SKILL.md` inside it, pinned by a boundary fixture holding the directory without the file, where the two predicates disagree.

### AC5

- **Given** the consuming-project fixture from AC1
- **When** the close report's doc-surface row is rendered through `sprint_report`
- **Then** it reports the row as not applicable rather than `unreadable`, so the identical
  permanent advisory does not survive in the report after being removed from the gate.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py -k doc_surface_row_is_not_applicable_outside_the_skill_repo
- **Verified:** yes (2026-08-09)
- **Mutant:** in `sprint_report.py`, restore the bare `verb_coverage` call in `_ck_doc_surface` without the applicability guard.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `gate.py`, delete the applicability guard from `_doc_surface` so it calls the measurement unconditionally | |
| AC2 | in `command_audit.py`, change `verb_coverage` to consult the gate's applicability predicate before measuring | |
| AC3 | in `gate.py`, narrow `_doc_surface`'s `except Exception` to `except ModuleNotFoundError` and return the not-applicable result from it | |
| AC4 | in `gate.py`, replace the shared call with a DIVERGENT inline copy testing for the skill directory rather than for `SKILL.md` inside it | |
| AC5 | in `sprint_report.py`, delete the applicability guard from `_ck_doc_surface`, leaving the bare measurement call | |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-09 | sdlc-studio | Filed |
