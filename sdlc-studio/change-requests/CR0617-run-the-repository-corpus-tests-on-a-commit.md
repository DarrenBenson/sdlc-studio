# CR-0617: Run the repository-corpus tests on a commit that changes artefacts, not only at push

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .githooks/pre-commit, .claude/skills/sdlc-studio/scripts/gate.py, tools/tests/test_pre_commit_corpus_selection.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** CI run 37640626017 on 34a7ee59; fix e2090297.
> **Date:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T15:37:22Z

## Summary

The commit hook selects test modules by direct import edges, so an artefact-only commit runs no suite ('docs, artefacts, hooks ... run no unit suite here; the full suite at push catches them'). But about twenty modules read the repository's own artefacts (they check `workspace.in_dev_repo()`), and an artefact can break them: on 2026-10-07 three bug texts filed in 815e5c04 tripped `test_shell_hazard_rate::test_no_legitimate_artefact_field_is_flagged`, and main went red at 34a7ee59 (CI run 37640626017). The push gate would have caught it, but on a loaded machine that gate took 52-60 minutes and failed on timing (BG0963), so the push went out with --no-verify. The twenty corpus modules ran in under five minutes on a quiet machine; the hazard test alone in under a second.

## Impact

Every artefact commit, from this session and from every consuming project's agent filing upstream; the corpus tests are the only thing between such a commit and CI when the push gate is slow or bypassed.

## Acceptance Criteria

- [ ] A commit that changes any file under sdlc-studio/ runs the repository-corpus test modules, or the cheap subset of them, before it lands
- [ ] A commit touching only code still selects by import edges as today
- [ ] The selection names the corpus modules it ran and their time, within the commit budget

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | sdlc-studio | Raised |
