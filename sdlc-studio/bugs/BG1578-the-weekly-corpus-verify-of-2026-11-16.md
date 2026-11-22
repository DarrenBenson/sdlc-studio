# BG1578: The weekly corpus verify of 2026-11-16 read US0926 AC1 and US0996 AC3 red on CI, and both pass locally at HEAD

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .github/workflows/lint.yml, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, changelog.d/BG1578.md, .claude/skills/sdlc-studio/scripts/tests/test_corpus_verify_red_detail.py
> **Evidence:** `https://github.com/DarrenBenson/sdlc-studio/actions/runs/43869298579`
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T02:44:12Z

## Summary

Scheduled Lint run 43869298579 (2026-11-16, at e356db80) failed corpus-verify with red-criteria 2 against a baseline of 0: NEW US0926::AC1 and US0996::AC3. Run sixteen read it when BG1518's new pre-push check refused the push. Both criteria pass at HEAD on the workstation (`verify_ac` run --dry-run: US0926 2/2, US0996 4/4). US0926 AC1's migrate.py check was seen to time out once under load during run sixteen, so CI's runner speed is the first suspect for it; US0996 AC3's CI failure is not explained, and the job log prints no detail for it.

## Steps to Reproduce

gh run view 43869298579 --log-failed; then run `verify_ac.py` run --id US0926 and --id US0996 on a CI-sized runner.

## Proposed Fix

Make corpus-verify print each red criterion's verifier output, and give US0926 AC1's check a budget measured on the runner.

## Acceptance Criteria

- [ ] **AC1** Given a corpus verify run in which a criterion is red, when `bash tools/verify-corpus.sh full` runs, then the job output prints that criterion's id and the verifier's own output under it, so the red can be read without re-running. Fails on: the red criteria named only by id, with no detail in the log.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_corpus_verify_red_detail.py::CorpusVerifyRedDetailTests

- [ ] **AC2** Given US0926 AC1's migrate.py check on a runner slower than the workstation, when `python3 .claude/skills/sdlc-studio/scripts/verify_ac.py run --id US0926` runs, then the check's time budget is the one the runner's measured speed sets, and it passes within it. Fails on: a fixed budget that timed out once under load.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_corpus_verify_red_detail.py::CorpusVerifyBudgetTests

## Impact

A weekly red that reads as flake teaches the operator to acknowledge it unread, which BG1518 exists to stop.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
| 2026-11-22 | Claude Sonnet 5.5 (qa seat, groom) | Acceptance criteria authored for planning (run twenty-two) |
