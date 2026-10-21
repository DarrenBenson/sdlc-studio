# CR-0637: The test suite's private temp root follows TMPDIR, so on a tmpfs /tmp every fixture repository copy is held in RAM and a killed run's tree is never freed

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** conftest.py, tools/skill-tests.sh, tools/tests/test_suite_temp_root.py, AGENTS.md
> **Date:** 2026-10-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (triage); human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-12T12:27:33Z

## Summary

`conftest.py:66-76` makes the suite's private root with `tempfile.mkdtemp(prefix='sdlc-tests-')` under the inherited TMPDIR, and `tools/skill-tests.sh:63` does the same with `${TMPDIR:-/tmp}`. On a workstation whose /tmp is a tmpfs (this repo's development machine: `findmnt -no FSTYPE /tmp` is tmpfs, 6.8 GB), every fixture write is RAM. Five test modules copy the whole repository (303 MB without .git), up to eight xdist workers run at once, and a run the harness kills leaves its root behind, still resident: on 2026-10-12, /tmp held two stale sdlc-tests roots (187 MB) and 2.7 GB of an agent session's scratch copies, on a 14 GB machine whose background jobs were being stopped for low memory.

## Impact

Anyone running the suite on a tmpfs /tmp, which is the default on several Linux distributions: the suite's footprint is counted against RAM, which raises the memory pressure that gets the gate killed (CR0635), and killed runs leak it until reboot.

## Acceptance Criteria

- [ ] Given TMPDIR unset and /tmp a tmpfs, when the suite starts, then its private root is created on a disk-backed directory (a documented default under the user's cache) and the run says where
- [ ] Given an explicit TMPDIR, when the suite starts, then it is honoured unchanged
- [ ] Given a stale private root left by a killed run, older than the newest run and owned by no live process, when the next run starts, then it is removed and named

## Recommendation

Until it ships: run the suite and the hooks with TMPDIR on disk (`export TMPDIR=$HOME/.cache/sdlc-tmp`).

## Triage (2026-10-21)

Kept (D0387). To plan it:

- Refine needs: one story, Points 3
- One Verify per criterion into the new tools/tests/test_suite_temp_root.py (disk-backed default when TMPDIR unset on tmpfs; explicit TMPDIR honoured; stale root removed and named)
- Affects adds changelog.d/<story>.md
- Persona: Rowan Achterberg (repo-only tooling, D0379)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | Claude Opus 5.5 (triage) | Raised |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
