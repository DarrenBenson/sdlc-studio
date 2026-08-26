# CR-0561: the declared Python 3.10 floor is stated in six shipped places and guarded nowhere, and one shipped script already violates it

> **Status:** Proposed
> **Priority:** High
> **Type:** enhancement
> **Size:** S
> **Affects:** tools/check_python_floor.py, tools/tests/test_check_python_floor.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .githooks/pre-commit, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** Adversarial review of BG0618, wave 2 of RUN-01M0YXN3, 2026-08-26. Both violations confirmed by compiling under a real python3.10 - the BG0618 one against working tree and HEAD to establish it as a regression, the sprint_report.py one against HEAD to establish it as pre-existing.
> **Date:** 2026-08-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Python 3.10+ is the floor in `README.md`, `SKILL.md`'s machine-readable `compatibility` field, `CONTRIBUTING.md`, `AGENTS.md`, the TRD, the TSD and `best-practices/python.md`. Nothing checks it. `.github/workflows/lint.yml` pins 3.12, the gate runs whatever `python3` is on the box, and no lane parses the tree at the floor. Measured 2026-08-26: sweeping the tracked scripts under a real python3.10, `sprint_report.py:420` ALREADY fails at HEAD on a nested same-quote f-string. A second violation reached review the same day - a backslash inside an f-string expression in `critic.py`, legal only from 3.12 (PEP 701) - and was caught by an adversarial reviewer rather than by any check. Both are import-time SyntaxErrors, not degraded features: every consumer on Ubuntu 22.04, which ships 3.10, loses the script entirely.

## Impact

A floor stated in six places and checked in none is a claim about compatibility that nobody has tested. The consequence is not a subtle behaviour difference - it is `import` raising, so a consuming project on the interpreter its distribution ships gets no script at all. It went unnoticed at HEAD, and the second instance was found by a human-equivalent reviewer reading a diff rather than by anything mechanical.

## Acceptance Criteria

- [ ] Given a tracked script using syntax newer than the declared floor, when the gate runs, then it is REFUSED and the file and line are named - the floor is stated in six shipped places and this is what makes any of them true
- [ ] Given every tracked script parses at the floor, when the lane runs, then it is silent - the paired control, so a lane that always fires does not get switched off
- [ ] Given `sprint_report.py` as it stands at HEAD, when the lane first runs, then it FAILS on it - a floor guard whose first execution over the real tree finds nothing has not been shown to look

## Steps to Reproduce

1. `python3.10 -c "import ast, pathlib; ast.parse(pathlib.Path('.claude/skills/sdlc-studio/scripts/sprint_report.py').read_text())"` against HEAD. 2. It raises SyntaxError at line 420. 3. Nothing in `npm run lint`, `gate.py` or CI reports it.

## Proposed Fix

Add a floor lane that parses every tracked `.py` at the declared version and refuses on a SyntaxError. `ast.parse(src, feature_version=...)` is NOT sufficient - it gates grammar rather than f-string tokenisation, so on a 3.12+ interpreter it accepts the very syntax 3.10 rejects, which a first cut of BG0618's own test discovered the hard way. Either invoke a real floor interpreter when one is present, or scan the AST for the specific constructs that post-date the floor. Repair `sprint_report.py:420` in the same change, or the lane lands red.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-26 | sdlc-studio | Raised |
