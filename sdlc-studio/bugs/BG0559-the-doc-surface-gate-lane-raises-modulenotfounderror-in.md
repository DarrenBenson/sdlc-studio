# BG0559: the doc-surface gate lane raises ModuleNotFoundError in every consuming project, so a new v5 lane reports NOT MEASURED forever on every user's gate run

> **Status:** Open
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/command_audit.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py
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

- [ ] **AC1** `gate.py --root <consuming project>` reports the doc-surface lane as not applicable with count 0, proven on a fixture that is not the skill repo and holds no lib/surface.py
- [ ] **AC2** `gate.py` run against a skill-repo tree still measures verb coverage and reports a real count, proving the lane was made inapplicable rather than switched off (positive control)
- [ ] **AC3** An unexpected fault inside the skill repo still reports NOT MEASURED with count 1, and the not-applicable and not-measured states are distinguishable in the lane's output
- [ ] **AC4** The applicability question has ONE reader shared with the doc-coverage lane, and the test proves the sharing by changing that reader and asserting both lanes follow

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | remove the applicability guard from `_doc_surface` - the consuming-project fixture must go from N/A back to NOT MEASURED with count 1 | `gate.py --root <consuming project>` reports the doc-surface lane as not applicable with count 0, proven on a fixture that is not the skill repo and holds no lib/surface.py |
| AC2 | make the applicability guard always return False - the skill-repo fixture must stop reporting a real verb count, and the test must fail | `gate.py` run against a skill-repo tree still measures verb coverage and reports a real count, proving the lane was made inapplicable rather than switched off (positive control) |
| AC3 | widen the applicability guard to swallow the in-repo import fault as not-applicable - the injected-fault test must fail | An unexpected fault inside the skill repo still reports NOT MEASURED with count 1, and the not-applicable and not-measured states are distinguishable in the lane's output |
| AC4 | give `_doc_surface` its own copy of the is-skill-repo predicate - changing the shared reader must stop moving both lanes, and the test must fail | The applicability question has ONE reader shared with the doc-coverage lane, and the test proves the sharing by changing that reader and asserting both lanes follow |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-09 | sdlc-studio | Filed |
