# BG1724: BG0974 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_filing_markdown_safe_title.py, changelog.d/BG0974.md
> **Created:** 2026-11-23
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-23T09:02:57Z

## Summary

BG0974 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] The link-destination exemption takes any bracket followed by a parenthesis as a link, so AC3 fails again for a title that is not a link: `_LINK_DEST_RE` (file\_finding.py:1682) matches a closing bracket, an open paren and anything up to the next `)`, including a parenthetical holding spaces, which CommonMark never reads as a link destination. Filed through `file_finding.py file`, the title `arr[0](_a and _b) differs` is written bare in the H1 and in the index row, and markdownlint under the skill's config refuses both lines (MD037 twice). A Python-shaped title such as `handlers[kind](_row, _seat) drops the seat` is refused the same way (MD037). That is AC3's own shape, two leading-underscore identifiers. Round one's `_md_safe` (2d716316) spans `_a`, `_b`, `_row` and `_seat` in both titles, so this round's exemption brought the failure back. A destination never holds unescaped whitespace outside angle brackets, so the pattern can stop at whitespace; [pre-existing] An Evidence value holding an inline metadata run, `see my_mod.py:3 · \*\*Waived:\*\* yes`, is read back by `extract_field` as a `Waived` field at the base ref and at HEAD alike: no open bug covers it; [pre-existing] BG1719 `artifact.py new` and `batch`, and the `triage_noise` consolidator, still write bare titles; RULINGS: Round one's finding "A markdown link whose destination holds an underscored file name is broken" is CLOSED: rerun with the same input through `file_finding.py file`, the Evidence value and the title each keep `[the filer test](scripts/tests/test_file_finding.py)` as a working link in the H1, the index row and the Evidence line, the link text is still safed, and both files lint clean. An image destination and a destination with a fragment are also kept. AC1, AC2 and AC3 pass at HEAD (verify\_ac dry-run, 3 of 3). The 85 test modules that import the filer or the creator run 3593 passed and 3 skipped (boundary-only) in a detached worktree with markdownlint on PATH. With markdownlint on PATH the replayed author mutant "test: lint under a config that is not there" is killed (1 failed), so its survival in the replay was a skip. My own mutant that exempts no destination is killed (3 failed).

## Steps to Reproduce

1. Read the round 2 REJECT of BG0974 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG0974 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] The link-destination exemption takes any bracket followed by a parenthesis as a link, so AC3 fails again for a title that is not a link: `_LINK_DEST_RE` (file\_finding.py:1682) matches a closing bracket, an open paren and anything up to the next `)`, including a parenthetical holding spaces, which CommonMark never reads as a link destination. Filed through `file_finding.py file`, the title `arr[0](_a and _b) differs` is written bare in the H1 and in the index row, and markdownlint under the skill's config refuses both lines (MD037 twice). A Python-shaped title such as `handlers[kind](_row, _seat) drops the seat` is refused the same way (MD037). That is AC3's own shape, two leading-underscore identifiers. Round one's `_md_safe` (2d716316) spans `_a`, `_b`, `_row` and `_seat` in both titles, so this round's exemption brought the failure back. A destination never holds unescaped whitespace outside angle brackets, so the pattern can stop at whitespace
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** The round 2 REJECT finding no longer holds: [pre-existing] An Evidence value holding an inline metadata run, `see my_mod.py:3 · **Waived:** yes`, is read back by `extract_field` as a `Waived` field at the base ref and at HEAD alike: no open bug covers it
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC3** The round 2 REJECT finding no longer holds: [pre-existing] BG1719 `artifact.py new` and `batch`, and the `triage_noise` consolidator, still write bare titles
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC4** BG0974 AC1 still passes: A finding titled with a bare `snake_case` identifier is written with that identifier inside a code span in its H1 and in its index row, so no `_` outside a code span remains on either line
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_filing_markdown_safe_title.py -k title_identifier_is_code_spanned
- [ ] **AC5** BG0974 AC2 still passes: An Evidence value holding such an identifier is written with it inside a code span, and its text otherwise reads byte-identical
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_filing_markdown_safe_title.py -k evidence_identifier_is_code_spanned
- [ ] **AC6** BG0974 AC3 still passes: (carried from BG1423) Given a finding title holding two identifiers that begin with underscores, when it is filed, then the bug file and the index row pass markdownlint. Fails on: an MD037 error on either.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_filing_markdown_safe_title.py::TitleMarkdownTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-23 | sdlc-studio | Filed |
