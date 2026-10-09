# BG1005: A pytest Verify that PARTLY skips is stamped green - BG0317 closed only the all-skipped case

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac_partial_skip.py, .claude/skills/sdlc-studio/help/verify.md, changelog.d/BG1005.md
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-09T07:15:34Z

## Summary

Found in homelab RUN-01M4EMNN (BG0259/BG0260 review). A Verify selecting a structural test and a render test ran '1 passed, 1 skipped' under the gate's pytest (no jinja2, the render test used pytest.importorskip) and was stamped Verified: yes - the behaviour the AC names was never executed where the gate runs; the author's venv ran it, so the mutation proof held only outside the gate. BG0317 made an ALL-skipped run vacuous; a mixed run still reads as a pass.

## Steps to Reproduce

Write two tests matched by one -k selector, one of them calling pytest.importorskip on a module the system python lacks; Verify: pytest <file> -k <selector>; run `verify_ac.py` run --id <unit> - it reports pass and stamps Verified: yes on '1 passed, 1 skipped'.

## Proposed Fix

Treat any skipped test in a pytest Verify run as not-verified (or 'partial' with the skipped ids named), on both the per-AC and the batch/JUnit paths; an explicit opt-in marker could allow a deliberate platform skip.

## Acceptance Criteria

- [ ] **AC1** A pytest Verify whose run passes some tests and skips others is not stamped `Verified: yes`, and `verify_ac run` names each skipped test and why
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac_partial_skip.py::PartialSkipTests::test_a_partly_skipped_run_is_not_verified
- [ ] **AC2** The same holds on the batch path that reads a JUnit report, so neither route stamps a partly skipped run
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac_partial_skip.py::PartialSkipTests::test_the_junit_path_reads_a_partial_skip_as_unverified

## Triage

- Reproduced at 750cbd81: a story whose Verify is `pytest tests/test_mixed.py -k partial`, matching one passing test and one that calls `pytest.importorskip` on an absent module, runs as `ac=1 pass=1` and is stamped `Verified: yes`. BG0317 made an all-skipped run vacuous; a mixed run still reads as a pass. Pre-existing.
- Severity Medium stands: the criterion's behaviour never ran where the gate runs. Affects corrected to repository paths; the tool-derived `pytest tests/ -k` selector replaced with a new test module (BG0980).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Filed |
| 2026-10-09 | Claude Opus 5.5 (triage) | Triaged: reproduced on current code; Affects made repository paths; criteria made executable |
