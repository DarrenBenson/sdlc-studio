# BG1054: The scheduled corpus-verify lane reads US0892 AC1 red because its job installs no pytest-xdist

> **Status:** In Progress
> **Severity:** Medium
> **Points:** 3
> **Affects:** .github/workflows/lint.yml, tools/verify-corpus-baseline.txt, sdlc-studio/stories/US0985-v6-1-0-is-cut-version-changelog-known.md, tools/tests/test_corpus_verify_env.py, changelog.d/BG1054.md
> **Evidence:** US1004 round-3 QA verdict (sdlc-studio/reviews/critic-verdicts.md), its [pre-existing] item, reproduced in a venv; scheduled Lint run 38246079155 at b3dcc041.
> **Created:** 2026-10-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-14T12:40:18Z

## Summary

lint.yml's corpus-verify job installs a shorter package list without pytest-xdist (kept out to protect the baseline comparison, lint.yml:178-180). US0892 AC1's verifier skips without xdist, and `verify_ac` reads an all-skipped verifier as FAIL ('every selected test was SKIPPED'), so the lane reports US0892::AC1 as NEW against a banked baseline of 0. Scheduled run 38246079155 at b3dcc041 (2026-10-12) named it beside US0940::AC1, US0957::AC3 and US0985::AC2, none recorded by an open Bug or CR. The comparison the omission protects is red because of the omission.

## Steps to Reproduce

In a venv holding exactly corpus-verify's install (lint.yml:181), run `verify_ac.py run --id US0892`: AC1 FAIL, every selected test SKIPPED; with pytest-xdist added, 2/2 pass.

## Proposed Fix

Decide the lane's intent and make one reading: either install pytest-xdist in corpus-verify (re-banking the baseline once), or have `verify_ac` read a verifier skipped for a missing optional plugin as UNVERIFIABLE rather than FAIL; then triage US0940::AC1, US0957::AC3 and US0985::AC2 from the same run.

## Acceptance Criteria

- [ ] **AC1** Given the corpus-verify job's own install, when it verifies US0892, then AC1's verifiers run rather than skip, because the job installs pytest-xdist from the declared list
  - **Verify:** pytest tools/tests/test_corpus_verify_env.py::CorpusVerifyEnvTests::test_the_job_installs_the_plugin_us0892_needs
- [ ] **AC2** Given US0957 AC3's `pdftotext` verifier, when the corpus-verify job runs it, then the job's own steps have installed the tool
  - **Verify:** pytest tools/tests/test_corpus_verify_env.py::CorpusVerifyEnvTests::test_the_job_installs_the_pdf_tool_us0957_runs
- [ ] **AC3** Given a High defect filed after v6.1.0 was cut, when US0985 AC2's verifier runs, then it still passes: its verifier is re-pointed to the cut's committed record rather than the live backlog's bar. The criterion is not retired, because `known_issues.py bar` survives and the criterion still pins it (LC-015)
  - **Verify:** pytest tools/tests/test_corpus_verify_env.py::CorpusVerifyEnvTests::test_us0985_ac2_does_not_redden_on_a_later_defect
- [ ] **AC4** Given US0940 AC1's verifier (276 s on a developer machine), when the corpus-verify job runs it, then its per-verifier ceiling clears the verifier's time as measured on the runner, with the measured run id and headroom recorded beside the ceiling, or the verifier is made faster
  - **Verify:** pytest tools/tests/test_corpus_verify_env.py::CorpusVerifyEnvTests::test_the_ceiling_clears_the_slowest_measured_verifier
- [ ] **AC5** Given the repaired job, when it runs on a dispatched workflow, then corpus-verify reports red criteria at the baseline with no NEW entry
  - **Verify:** manual: dispatch lint.yml (`gh workflow run lint.yml`) and read the corpus-verify job's `red-criteria:` line

## Notes

- Diagnosed 2026-10-19 against scheduled run 38246079155 (`NEW: US0892::AC1 US0940::AC1 US0957::AC3 US0985::AC2`). US0957 AC3 and US0940 AC1 pass on a developer machine (`pdftotext` installed; 275.7 s), so both are environment gaps in the job. US0985 AC2 fails everywhere: `known_issues.py bar` reads the live backlog, which BG0962 and BG1000 (High, filed after the cut) now fail, so a Done story's criterion reddens whenever a later defect is filed.
- Chosen reading for US0892: install pytest-xdist in the job, as the ci job already does, rather than teaching verify_ac a second meaning of a skip; re-bank the baseline only if the measured count moves.
- AC1 must fail on: the job's install line losing pytest-xdist. AC2 must fail on: the job installing no `pdftotext`. AC3 must fail on: the verifier reading `known_issues.py bar` against the working tree. AC4 must fail on: a ceiling below the measured verifier time.
- AC5 is manual, so the dispatched run's id and its `red-criteria:` line are recorded on this bug before it is moved to Fixed. It runs last in the batch so the run reads every criterion the batch adds.
- Rescoping: dispatched run 39226633444 at 35a795df (2026-10-19) reads the current red set; the criteria this bug answers are re-read from it before delivery, since the scheduled run it was filed against predates 48 commits.
- Widened on 2026-10-19 from US0892 alone to the four NEW criteria of the same run, as the operator ruled (D0377); re-pointed 2 to 3.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-14 | sdlc-studio | Filed |
| 2026-10-19 | Claude Opus 5.5 | Groomed for the second 6.2 run (D0377): the four NEW criteria, Verify lines, re-pointed 3 |
| 2026-10-19 | Claude Opus 5.5 | Regroomed after the goal review (round 4): the seats' findings folded in: re-point not retire (AC3), runner-measured headroom (AC4), run id before Fixed (AC5), last in the batch |
