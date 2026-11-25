# BG1304: `artifact.py new` wraps a file name inside a path in backticks, so tools/tests/x.py in a CR's Impact or criteria is written as tools/tests/`x.py`

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_filing_markdown_safe_title.py, changelog.d/BG1304.md
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

- [ ] **AC1** Given a fields file whose impact, summary and one criterion each name a path with a directory in prose (the tools/tests path of a test module), when `artifact.py new --type cr --fields-file` writes the request in a scratch root, then each section holds the path whole, inside one code span or untouched, and nowhere a directory followed by a backticked file name. Fails on: one path split into prose and a code span, which breaks a reader's copy of it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::SuppliedContentLandsTests::test_a_path_with_a_directory_is_never_split_by_a_code_span
- [ ] **AC2** Given the one prose escaper, `file_finding._md_safe`, when it is given a slash-joined path, a bare underscored identifier and a path already inside a code span, then the path comes back as one token, the identifier is still wrapped and the spanned path is unchanged. Fails on: the fix switching off the identifier pass, or re-wrapping a span.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::MdSafeProseTests::test_a_slash_joined_path_is_one_token

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
| 2026-11-25 | orchestrator (delegate under D0545) | Affects widened for the carry round (BG1744): the one-segment rooted path is pinned through `file_finding.py file` in the filer's title and body test, beside the other markdown-safe filing cases |
