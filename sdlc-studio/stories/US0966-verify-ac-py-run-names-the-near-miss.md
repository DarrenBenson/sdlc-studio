# US0966: `verify_ac.py run` names the near-miss node when a Verify selector's file is collected but its node is not

> **Status:** Ready
> **Delivers:** CR0559
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_run_near_miss_hint.py, changelog.d/US0966.md
> **Epic:** EP0244
> **Points:** 1
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** a FAIL from a mistyped Verify selector to name the test I most likely meant
**So that** the first red run fixes the typo instead of sending me to grep the test file

## Summary

Groomed under D0291 (sdlc-studio/reviews/backlog-sweep-2026-10-01.md), 1 point; this was CR0563, merged into CR0559. `verify_ac.selector_near_miss` already computes the hint (verify_ac.py:1042) and only `file_finding` calls it (file_finding.py:498, 573). `verify_ac run` prints pytest's `not found` lines and nothing else. The fix calls the existing function on a pytest FAIL whose output carries `not found` and prints its answer under the FAIL line; no new check, refusal or report field.

## Premise at HEAD

Executed at `85042135` against a scratch fixture holding `tests/test_probe.py::ProbeTests::test_alpha` and a story whose Verify line names `ProbTests`:

```text
$ verify_ac.py run --story sdlc-studio/stories/US0001-probe.md --dry-run --root <fixture>
[DRY] US0001-probe.md: ac=1 pass=0 fail=1 manual=0 unspecified=0 changes=0
        FAIL AC1: pytest tests/test_probe.py::ProbTests::test_alpha
          | ERROR: not found: <fixture>/tests/test_probe.py::ProbTests::test_alpha
          | (no match in any of [<Module test_probe.py>])
exit=1
$ python3 -c "import verify_ac; print(verify_ac.selector_near_miss('pytest tests/test_probe.py::ProbTests::test_alpha', cwd='<fixture>'))"
did you mean tests/test_probe.py::ProbeTests::test_alpha
```

## Acceptance Criteria

- [ ] **AC1** Given a fixture whose test file collects `ProbeTests::test_alpha` and a story whose Verify line names `ProbTests::test_alpha`, when `verify_ac.py run --story <story> --dry-run --root <fixture>` runs, then the FAIL block for AC1 carries `did you mean tests/test_probe.py::ProbeTests::test_alpha`. Fails on: HEAD prints only pytest's `not found` lines
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_run_near_miss_hint.py::RunNearMissHintTests::test_a_mistyped_class_names_the_collected_node
- [ ] **AC2** Given the same fixture with a Verify line naming the real node of a test that fails on an assertion, when `verify_ac.py run` reports it FAIL, then no `did you mean` line is printed. Fails on: printing a hint on every FAIL rather than only on a node that was not found
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_run_near_miss_hint.py::RunNearMissHintTests::test_a_failing_real_node_gets_no_hint

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-01 | engineering seat (groomer) | Groomed under D0291 (backlog sweep 2026-10-01): criteria authored, premise executed at HEAD 85042135, Points and Affects set |
