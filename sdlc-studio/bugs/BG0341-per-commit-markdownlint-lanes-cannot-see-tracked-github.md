# BG0341: Per-commit markdownlint lanes cannot see tracked .github/ markdown; only the excluded weekly corpus job covers it

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Low
> **Points:** 2
> **Affects:** .githooks/pre-commit
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5); agent; skill v5.0.0
> **Audit-lens:** unknown
> **Audit-run:** wf_d141ccb5

## Summary

The hook's **/*.md glob cannot enter dot-directories (its own comment says so) and the remediation lane enumerates exactly one (.claude/**/*.md); three tracked markdown files under .github/ match neither glob in the hook nor in CI lint:md, so a markdown defect there passes every per-commit and per-push lane, and the hook's Node-absent SKIP message ('CI still enforces it') is untrue for these files - only the schedule-only corpus job sees them.

## Steps to Reproduce

Evidence (markdown lanes, lines 310-324; same globs in package.json lint:md (line 8)): pre-commit 314 globs **/*.md, 315-316 comment names the dot-directory blindness, 323 adds only .claude/**/*.md; package.json repeats both globs; git ls-files shows .github/`PULL_REQUEST_TEMPLATE.md` and two `ISSUE_TEMPLATE` files; lint.yml corpus job runs only on schedule/`workflow_dispatch.`

## Proposed Fix

Add '.github/**/*.md' to both the hook lane and package.json lint:md (kept in sync), or better, feed markdownlint the file list from git ls-files '*.md' so every tracked dot-directory is covered without per-directory enumeration.

## Acceptance Criteria

### AC1: tracked markdown under a dot-directory is linted per commit

- **Given** the defect as filed in Steps to Reproduce
- **When** the repair is in place
- **Then** the behaviour is the one the Proposed Fix describes, proven by a test written red before the fix
- **Proven by:** pytest tools/tests/test_message_first_gate.py::MarkdownLaneTests
- **Verified:** yes (2026-07-28, functional)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5) | Filed |
| 2026-07-28 | Claude Fable 5 | Acceptance criterion authored at review - the unit reached Fixed without one, which CR0459 exists to refuse |
