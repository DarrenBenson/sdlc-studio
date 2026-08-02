# BG0490: four bug repairs are Fixed with half their title undelivered and no recorded narrowing

> **Status:** Open
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Provenance:** dogfood
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/bugs, tools/check_links.py, .claude/skills/sdlc-studio/templates/audit-profiles/code.md, tools/check_versions.py, .githooks/pre-commit
> **Severity:** Medium
> **Points:** 5

## Summary

Independent passes over RUN-01KYZKY5 found four bugs recorded Fixed while a defect named in their own title or Proposed Fix is still present. BG0433 and BG0448, in the same batch, DID carve their undelivered halves out explicitly (into BG0486 and BG0485), so the practice exists and these four departed from it.

BG0434 - title and step 3 promise 'the one real row's path resolves anywhere'. `templates/audit-profiles/code.md:17` still ends in a full stop. No AC, no carve-out, no decline note.

BG0435 - title promises 'nine of twelve broken-path shapes escape it'. Measured against the shipped classifier: `scripts/rg-wrapper-DOES-NOT-EXIST.py` classifies as `invocation` and is skipped (`_INVOCATION` at `check_links.py`:356 is still an unanchored `re.search`); `notes/X.txt` and `tools/X.toml` classify as `prose` and are skipped (`_PATH_CELL:358` still allowlists six extensions). Three of four items in its own Proposed Fix are undelivered.

BG0462 - names three defects, ships one. `.githooks/pre-commit`'s `run()` still discards `$out` on a zero exit; `tools/check_versions.py:5` still states 'structure from exactly five places - never by repo-wide grep', which the bug itself records as false. Both paths are in its declared Affects and untouched.

BG0437 - the prose claim is corrected in 307ce91d; listed here only so the set is complete.

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
