# US1002: Filing into the skill source refuses a blocklisted project name before an id is spent

> **Status:** Draft
> **Delivers:** CR0612
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, tools/check_neutrality.py, tools/tests/test_filing_neutrality.py, .claude/skills/sdlc-studio/reference-scripts-create.md, changelog.d/US1002.md
> **Epic:** EP0277
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As** a founder-engineer whose agents in consuming projects file bugs and CRs straight into the skill source repository
**I want** `file_finding.py file` to run the target repository's neutrality check over the artefact it is about to write, and refuse before minting an id when that text names a blocklisted project or when the check cannot give a clean answer
**So that** the agent that wrote the prose rewrites it while it still holds the context, and no later session has to generalise somebody else's filing before it can commit

## Acceptance Criteria

- **AC1:** Given a fixture root carrying `sdlc-studio/bugs/_index.md` and a copy of `tools/check_neutrality.py` with a sentinel word on its blocklist, when `file_finding.py file --type bug --root <fixture>` is run with that word in `--summary`, with and without `--dry-run`, then each run exits 1 with a `file refused` line naming the Summary section and the checker's redacted hash prefix (not the word) and ending with the fix (generalise it, for example to 'a consuming project'), and no artefact file or index row is written.
  - **Verify:** pytest tools/tests/test_filing_neutrality.py::FilingNeutralityTests::test_a_blocklisted_name_in_a_field_is_refused_before_any_write
- **AC2:** Given the same fixture, when the only occurrence of the word reaches the artefact through the author (`SDLC_AUTHOR` set to a name containing it, with clean fields), then the filing is refused naming the Raised-by field, because the check reads the text that would be written rather than the fields the caller passed.
  - **Verify:** pytest tools/tests/test_filing_neutrality.py::FilingNeutralityTests::test_a_name_arriving_only_through_the_author_is_refused
- **AC3:** Given a fixture root with no `tools/check_neutrality.py`, when the same filing naming the sentinel word is made, then it files exactly as today (exit 0, `filed BG0001`, the artefact on disk) and prints no line naming a neutrality checker it ran.
  - **Verify:** pytest tools/tests/test_filing_neutrality.py::FilingNeutralityTests::test_a_root_without_the_checker_files_as_today
- **AC4:** Given a fixture root whose `tools/check_neutrality.py` raises `RuntimeError` at import (exit 1, a traceback, no hit lines), when a clean filing is made, then it is refused as 'the neutrality check could not run', naming the checker and its exit code and naming no section, and nothing is written.
  - **Verify:** pytest tools/tests/test_filing_neutrality.py::FilingNeutralityTests::test_a_checker_that_crashes_is_reported_as_unable_to_run
- **AC5:** Given a fixture root carrying this repository's checker as it is at HEAD (which ignores `--stdin`, scans the tracked tree and exits 0) with the sentinel's hash on its blocklist, when a filing naming the sentinel is made, then it is refused as 'the neutrality check could not run', naming the checker and saying it does not support `--stdin`, and nothing is written.
  - **Verify:** pytest tools/tests/test_filing_neutrality.py::FilingNeutralityTests::test_a_checker_without_stdin_support_is_refused_not_read_as_clean

## Notes

- Release: 6.2 (D0355 breakdown G3, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the pre-mint neutrality call removed from file_finding.file_finding, or placed after the dry-run branch (today's code: the bug files as BG0001 and the commit lane is the first to object)
- AC2 must fail on: the check scans the caller-supplied fields (title, summary, steps, fix, criteria) but not the resolved authorship that `_file_finding_locked` stamps into Raised-by and the revision row
- AC3 must fail on: the filer falling back to a checker of its own (the skill's repository copy at parents[4]/tools/check_neutrality.py) when the target root carries none, which the filer's 'checked with <path>' line makes visible; or a missing checker treated as a refusal
- AC4 must fail on: exit 1 read as 'a blocklisted name was found' (a crash reported against a section), or any non-zero exit other than 1 read as clean
- AC5 must fail on: exit 0 read as clean without the `--stdin` mode's confirmation line (probed by the panel: today's checker answers stdin carrying a blocklisted word with 'neutrality: no blocklisted project names in tracked files', exit 0)
- Checker contract (the panel's required change). `python3 tools/check_neutrality.py --stdin` scans stdin with the existing `scan_text`. It prints one `<stdin>:<line> (redacted: <hash>)` line per hit and exits 1 when there are hits. When there are none it prints the fixed confirmation line `neutrality: stdin clean` and exits 0.
- The filer reads a hit only from hit lines, and a clean only from exit 0 plus the confirmation line. Everything else means the check could not run, and the filer refuses: exit 1 with no hit lines, any other exit, a timeout, or exit 0 without the confirmation line. An exit-2 checker is a second case in the AC4 class.
- Add `--stdin` to the checker's usage docstring (check_neutrality.py:17-18).
- Filer placement. The call goes in `file_finding()` after `check_groomed` and before `duplicate_candidates` and the allocation lock (file_finding.py:2193-2231). It runs when `<root>/tools/check_neutrality.py` is a file. Pipe the would-be artefact to `[sys.executable, checker, '--stdin']`, with cwd=root and a timeout.
- When the filer runs a checker it prints one line, `neutrality: checked with <path>`, which makes AC3's fallback mutant visible.
- Map each hit line to the nearest `##` heading or `> **Field:**` line above it. End the refusal with the fix, as the commit lane does.
- One helper (LL0016) takes the fields and returns them with the authorship (`sdlc_md.authorship_value`, which is pure) and the batch stamp resolved. Both the scanned preview and `_file_finding_locked`'s write use it, so the text checked is the text written. A field added later to the locked write cannot slip past the check.
- Fixture. Copy this repository's tools/check_neutrality.py and replace its `_BLOCKED` set with the SHA-256 of the sentinel `zzqsentinelname`, the word tools/tests/test_check_neutrality.py already uses. The filer is then tested against the real checker's CLI (LL0020).
- AC5 copies HEAD's checker as it stands today; the test can hold that copy as a fixture file, or take it with `git show <today's sha>:tools/check_neutrality.py`. Give every fixture an `_index.md`, because `file_finding` never creates one on this path, so 'no index row' would otherwise be vacuous.
- Probed at HEAD by the drafter and re-checked by the panel. A bug carrying the sentinel filed as BG0001 with exit 0, and the copied checker found three hits in it. With `SDLC_AUTHOR` carrying the sentinel, it was stamped into Raised-by (line 9) and the revision row (line 32).
- Consuming projects get this only once their installed copy carries it: the release, or `tools/forward-port.sh --yes` on this machine. A newer filer against an older checkout is AC5's case, and it refuses with the fix: update the checkout.
- reference-scripts-create.md (### file_finding.py) gains one sentence: filing into a root that carries tools/check_neutrality.py runs it over the would-be artefact before an id is minted, and refuses when it cannot run.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G3 after the refine panel's review |
