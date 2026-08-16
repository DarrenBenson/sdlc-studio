# BG0490: four bug repairs are Fixed with half their title undelivered and no recorded narrowing

> **Status:** Open
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Provenance:** dogfood
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/bugs, tools/check_links.py, .claude/skills/sdlc-studio/templates/audit-profiles/code.md, tools/check_versions.py, .githooks/pre-commit, tools/tests/test_check_links.py, tools/tests/test_check_versions.py
> **Severity:** Medium
> **Points:** 5

## Summary

Independent passes over RUN-01KYZKY5 found four bugs recorded Fixed while a defect named in their own title or Proposed Fix is still present. BG0433 and BG0448, in the same batch, DID carve their undelivered halves out explicitly (into BG0486 and BG0485), so the practice exists and these four departed from it.

BG0434 - title and step 3 promise 'the one real row's path resolves anywhere'. `templates/audit-profiles/code.md:17` still ends in a full stop. No AC, no carve-out, no decline note.

BG0435 - title promises 'nine of twelve broken-path shapes escape it'. Measured against the shipped classifier: `scripts/rg-wrapper-DOES-NOT-EXIST.py` classifies as `invocation` and is skipped (`_INVOCATION` at `check_links.py`:356 is still an unanchored `re.search`); `notes/X.txt` and `tools/X.toml` classify as `prose` and are skipped (`_PATH_CELL:358` still allowlists six extensions). Three of four items in its own Proposed Fix are undelivered.

BG0462 - names three defects, ships one. `.githooks/pre-commit`'s `run()` still discards `$out` on a zero exit; `tools/check_versions.py:5` still states 'structure from exactly five places - never by repo-wide grep', which the bug itself records as false. Both paths are in its declared Affects and untouched.

BG0437 - the prose claim is corrected in 307ce91d; listed here only so the set is complete.

## Triage 2026-08-15

Re-measured claim by claim before any code was written, on the operator's ruling that the audit
residue is triaged rather than built. **Two of the four instances have lapsed and two stand.**

| Instance | Claim | Measured now |
| --- | --- | --- |
| BG0434 | `templates/audit-profiles/code.md:17` still ends in a full stop | **LAPSED** - it does not |
| BG0435 | nine of twelve broken-path shapes escape the classifier | **STANDS** - `scripts/rg-wrapper-DOES-NOT-EXIST.py` is still skipped as an invocation, and `notes/X.txt` and `tools/X.toml` are still skipped as prose, reproduced against the shipped patterns |
| BG0462 | `.githooks/pre-commit`'s `run()` discards `$out` on a zero exit | **LAPSED** - `$out` is stashed on both paths, fixed under BG0239 |
| BG0462 | `check_versions.py:5` claims the version is read "never by repo-wide grep" | **STANDS** - the module falls back to `root.rglob("*.md")` when git cannot enumerate, so the docstring overstates |

Narrowed to those two. The lapsed pair is recorded rather than deleted, because "this was true and
is not" is the fact a later reader needs - a bug re-opened on a stale premise costs more than the
line it took to say so.

Not built here: the surviving half of BG0435 is a change to the link classifier's patterns, with
blast radius across every loading-guide cell, and that is engineering rather than triage.

## Acceptance Criteria

- [ ] **AC1** Given `templates/audit-profiles/code.md`, when its one real row is read, then the path resolves - the BG0434 half this bug carried, re-measured 2026-08-15 as ALREADY LAPSED and pinned so it cannot regress unnoticed.
  - **Verify:** pytest tools/tests/test_check_links.py::AuditProfilePathsTests::test_the_one_real_row_resolves
- [ ] **AC2** Given a broken path shaped like an invocation (`scripts/rg-wrapper-DOES-NOT-EXIST.py`) or carrying an unlisted extension (`notes/X.txt`, `tools/X.toml`), when the link classifier reads it, then it is REPORTED rather than skipped - the BG0435 half, which still reproduces.
  - **Verify:** pytest tools/tests/test_check_links.py::AuditProfilePathsTests::test_invocation_and_prose_shapes_are_not_skipped
- [ ] **AC3** Given `check_versions.py`'s docstring claim that the version is read 'never by repo-wide grep', when the module is read, then the claim matches the code - it falls back to `root.rglob('*.md')`, so today the docstring overstates.
  - **Verify:** pytest tools/tests/test_check_versions.py::DocstringMatchesTheCodeTests::test_the_never_by_grep_claim_is_true

## Steps to Reproduce

1. `grep -n 'ends in a full stop' templates/audit-profiles/code.md` - line 17 still does.
2. Classify the three path shapes above through tools/`check_links.py` - all three skip.
3. Read `run()` in .githooks/pre-commit - `$out` is still discarded on success.

## Proposed Fix

For each: either deliver the remaining half, or narrow the bug explicitly and file the residue as its own artefact, the way BG0433 and BG0448 did. A bug closed Fixed with its title still true of the tree is a false record, and the next reader takes the title as the statement of what was done.

## Impact

Four false Fixed records. The cost is not the individual defects - it is that a Fixed status stops meaning the title is no longer true, and every later reader who trusts the ledger inherits the error. The repo's close ceremony reads these statuses.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
