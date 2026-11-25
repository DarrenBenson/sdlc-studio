# BG1744: BG1304 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, changelog.d/BG1304.md
> **Created:** 2026-11-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M87B5M - raised during the run, 2026-11-25T01:36:44Z

## Summary

BG1304 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] The repaired changelog still over-states the rooted case: changelog.d/BG1304.md now says a file path, "a rooted one" among the forms it lists, is written as one code span rather than split into prose and a code-spanned file name, but the path shape of `_MD_TOKEN_RE` needs two segments after its root (file\_finding.py:1789-1791, as its own comment at :1784 says), so a rooted path of one segment falls through to the identifier shape. Filed through `file_finding.py file`, a summary reading "see ~/my\_file.txt and /tmp\_dir and ~/.cache/run\_x.json now" is written with the tilde-slash and the slash left outside spans that hold only `my_file.txt` and `tmp_dir`, exactly as at the base 74903e754, while the two-segment path beside them is spanned whole\; no test carries a rooted path of one segment, and a root followed by zero or more directories would close it; [pre-existing] The identifier shape is quadratic in a dotted run with no underscore: `ff._md_safe("a." * 8000 + "x")` takes 2.6 s at the base and 1.7 s after the repair, since that shape may start again after every dot (file\_finding.py:1792)\; no open bug covers it; RULINGS: Round one "The path token stops short of a path's root and of a directory-only underscore" is MOVED: `/abs/dir/test_x.py`, `~/.cache/sdlc-tmp/run_x.json`, `$HOME/bin/do_it` and `src/my_pkg/main.py` now each come back as one span, pinned in `test_a_slash_joined_path_is_one_token` (my mutant deleting the root group is KILLED), but a rooted path of one segment is still split, and the repair's changelog claims it is not. Round one "The directory prefix makes the escaper quadratic in a path's segment count" is CLOSED: `ff._md_safe("a/" * 16000 + "x")` takes 0.027 s after the repair against 45 s at round one, and `test_the_escaper_is_linear_in_a_paths_segment_count` passes when run by its node id (it is marked to run at the push, which the commit run leaves out). AC1 holds by execution: both Verify selectors pass, `verify_ac.py run --id BG1304 --dry-run` reports pass=2 fail=0, and the request carries the tools/tests path in one span in each section.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1304 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1304 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] The repaired changelog still over-states the rooted case: changelog.d/BG1304.md now says a file path, "a rooted one" among the forms it lists, is written as one code span rather than split into prose and a code-spanned file name, but the path shape of `_MD_TOKEN_RE` needs two segments after its root (file\_finding.py:1789-1791, as its own comment at :1784 says), so a rooted path of one segment falls through to the identifier shape. Filed through `file_finding.py file`, a summary reading "see ~/my\_file.txt and /tmp\_dir and ~/.cache/run\_x.json now" is written with the tilde-slash and the slash left outside spans that hold only `my_file.txt` and `tmp_dir`, exactly as at the base 74903e754, while the two-segment path beside them is spanned whole; no test carries a rooted path of one segment, and a root followed by zero or more directories would close it
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** The round 2 REJECT finding no longer holds: [pre-existing] The identifier shape is quadratic in a dotted run with no underscore: `ff._md_safe("a." * 8000 + "x")` takes 2.6 s at the base and 1.7 s after the repair, since that shape may start again after every dot (file\_finding.py:1792); no open bug covers it
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC3** BG1304 AC1 still passes: Given a fields file whose impact, summary and one criterion each name a path with a directory in prose (the tools/tests path of a test module), when `artifact.py new --type cr --fields-file` writes the request in a scratch root, then each section holds the path whole, inside one code span or untouched, and nowhere a directory followed by a backticked file name. Fails on: one path split into prose and a code span, which breaks a reader's copy of it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::SuppliedContentLandsTests::test_a_path_with_a_directory_is_never_split_by_a_code_span
  - **Verified:** yes (2026-11-25)
- [ ] **AC4** BG1304 AC2 still passes: Given the one prose escaper, `file_finding._md_safe`, when it is given a slash-joined path, a bare underscored identifier and a path already inside a code span, then the path comes back as one token, the identifier is still wrapped and the spanned path is unchanged. Fails on: the fix switching off the identifier pass, or re-wrapping a span.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::MdSafeProseTests::test_a_slash_joined_path_is_one_token
  - **Verified:** yes (2026-11-25)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-25 | sdlc-studio | Filed |
