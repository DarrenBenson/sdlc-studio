# BG1304: `artifact.py new` wraps a file name inside a path in backticks, so tools/tests/x.py in a CR's Impact or criteria is written as tools/tests/`x.py`

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
> **Evidence:** CR0689 as first written on 2026-11-09 (Impact and AC2, AC5 and AC6), corrected by hand before commit
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T12:03:22Z

## Summary

Filing CR0689 on 2026-11-09 with `artifact.py new --type cr --fields-file`, the Impact and three acceptance criteria named `tools/tests/test_persona_coherence.py` and `tools/tests/test_lean_prd_refresh.py` as bare paths. The written CR read `tools/tests/test_persona_coherence.py`: the identifier pass backticked the file name and left its directory outside the span, which splits one path into prose and code and breaks a reader's copy of the path. The paths were corrected by hand. BG0967 is the same pass corrupting the finding filer's Steps to Reproduce; this is `artifact.py new` on Impact and criteria prose. `file_finding.py file` does the same: this bug's own Summary, Steps and AC1 were written with the split paths on filing, and were corrected by hand.

## Steps to Reproduce

1. Write a fields file for `artifact.py new --type cr` whose impact reads: the test `tools/tests/test_persona_coherence.py` reads three roles.
2. Run artifact.py --root <scratch copy> new --type cr --fields-file <that file>.
3. Read the Impact section of the written CR: it says tools/tests/`test_persona_coherence.py`.

## Proposed Fix

Treat a slash-joined path as one token: wrap the whole path, or leave it unwrapped, never its last segment alone. Add a test that a path with a directory in Impact, Summary and an AC is written either whole inside one span or untouched.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Filing CR0689 on 2026-11-09 with `artifact.py new --type cr --fields-file`, the Impact and three acceptance criteria named...
- [ ] **AC2** The proposed fix lands, pinned by a test: Treat a slash-joined path as one token: wrap the whole path, or leave it unwrapped, never its last segment alone.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
