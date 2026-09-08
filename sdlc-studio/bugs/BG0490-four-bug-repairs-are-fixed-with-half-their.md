# BG0490: four bug repairs are Fixed with half their title undelivered and no recorded narrowing

> **Status:** Open
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Provenance:** dogfood
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/check_links.py, tools/tests/test_check_links.py, tools/check_versions.py, tools/tests/test_check_versions.py, .claude/skills/sdlc-studio/templates/audit-profiles/code.md
> **Severity:** Medium
> **Points:** 5
> **Verification depth:** functional (authored at plan time as the tier this unit is driven to; the derived half is written by `verify_ac.py depth --write` at delivery, never by hand)

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

> **What these criteria are.** They are the DELIVERY CONTRACT for the halves that still
> reproduce, not a claim that this run built them. The operator's ruling stands: these bugs
> are triaged, not built. What the design rung produced is criteria that fail RED now, so
> whoever delivers the fix inherits a falsifiable target instead of a summary. The one
> exception is called out where it sits: a criterion pinning a half that has already LAPSED
> is a regression pin, and it goes green the moment its test exists rather than when a fix
> lands.

- [ ] **AC1** Given `templates/audit-profiles/code.md`, when its signature rows are read, then AT LEAST ONE names a script and every script so named is on disk. The existence half is not decoration: a later edit turning that row to `manual - ...` leaves zero script-naming rows, and a test asserting only that the named ones resolve then passes on nothing. The BG0434 half, re-measured 2026-08-15 as ALREADY LAPSED and pinned here so it cannot regress unnoticed
  - **Verify:** pytest tools/tests/test_check_links.py::AuditProfilePathsTests::test_the_one_real_row_resolves
  - **Verified:** no
- [ ] **AC2** Given a guide cell naming a path whose extension is outside the six the classifier allows - `notes/X.txt`, `tools/X.toml` - when the cells are classified, then a MISSING one is reported and an EXISTING one is not. Today both fall through to `prose`, so an unlisted extension is a silent exemption rather than a decision
  - **Verify:** pytest tools/tests/test_check_links.py::LoadingGuideExemptionTests::test_an_unlisted_extension_is_resolved_rather_than_exempted
  - **Verified:** no
- [ ] **AC3** Given a cell that is an INVOCATION, when it is classified, then its kind is still `invocation` - the explicit-exemption contract the shipped classification test pins is unchanged - and the script path inside it is separately resolved, so a command naming a script that does not exist is reported while one naming a script that does is not. The shipped exemption test's empty-result assertion runs on a fixture whose command names a script that is not on disk, so resolving invocation scripts reddens it: that fixture is amended in the same change to name a script that exists, and its kind assertion is kept. Ruled here rather than discovered at the gate
  - **Verify:** pytest tools/tests/test_check_links.py::LoadingGuideExemptionTests::test_an_invocation_keeps_its_kind_and_its_script_is_resolved
  - **Verified:** no
- [ ] **AC4** Given an INVOCATION cell whose script IS on disk, and a prose cell naming no path at all, when the check runs, then neither is reported. This is the positive control the two rows above cannot supply between them: a classifier reporting every command it sees satisfies AC3 without resolving anything. The templated cell is deliberately not the control: measured, deleting the templated branch only moves the cell to `prose` and a braced path fails the path pattern either way, so that observable cannot move
  - **Verify:** pytest tools/tests/test_check_links.py::LoadingGuideExemptionTests::test_templated_and_prose_cells_are_still_exempt
  - **Verified:** no
- [ ] **AC5** Given `check_versions.py`, when its module docstring is read beside its code, then it does not claim the version is read 'never by repo-wide grep' while an `rglob` fallback stands. Today it does, so the docstring overstates the guarantee a reader relies on
  - **Verify:** pytest tools/tests/test_check_versions.py::DocstringMatchesTheCodeTests::test_the_never_by_grep_claim_is_true
  - **Verified:** no

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in .claude/skills/sdlc-studio/templates/audit-profiles/code.md, replace the ac-drift signature's command with a `manual - ...` note | Given `templates/audit-profiles/code.md`, when its signature rows are read, then AT LEAST ONE names a script and every script so named is on disk. The existence half is not decoration: a later edit turning that row to `manual - ...` leaves zero script-naming rows, and a test asserting only that the named ones resolve then passes on nothing. The BG0434 half, re-measured 2026-08-15 as ALREADY LAPSED and pinned here so it cannot regress unnoticed |
| AC2 | in tools/check_links.py, narrow the `_PATH_CELL` extension alternation back to the six shipped suffixes | Given a guide cell naming a path whose extension is outside the six the classifier allows - `notes/X.txt`, `tools/X.toml` - when the cells are classified, then a MISSING one is reported and an EXISTING one is not. Today both fall through to `prose`, so an unlisted extension is a silent exemption rather than a decision |
| AC3 | in tools/check_links.py, delete the `_INVOCATION` branch's script-token extraction and `continue` past the cell | Given a cell that is an INVOCATION, when it is classified, then its kind is still `invocation` - the explicit-exemption contract the shipped classification test pins is unchanged - and the script path inside it is separately resolved, so a command naming a script that does not exist is reported while one naming a script that does is not. The shipped exemption test's empty-result assertion runs on a fixture whose command names a script that is not on disk, so resolving invocation scripts reddens it: that fixture is amended in the same change to name a script that exists, and its kind assertion is kept. Ruled here rather than discovered at the gate |
| AC4 | in tools/check_links.py, emit a finding for every `_INVOCATION` cell without testing whether its script is on disk | Given an INVOCATION cell whose script IS on disk, and a prose cell naming no path at all, when the check runs, then neither is reported. This is the positive control the two rows above cannot supply between them: a classifier reporting every command it sees satisfies AC3 without resolving anything. The templated cell is deliberately not the control: measured, deleting the templated branch only moves the cell to `prose` and a braced path fails the path pattern either way, so that observable cannot move |
| AC5 | in tools/check_versions.py, reinsert the absolute phrasing into the module docstring while `root.rglob` stays in the resolver | Given `check_versions.py`, when its module docstring is read beside its code, then it does not claim the version is read 'never by repo-wide grep' while an `rglob` fallback stands. Today it does, so the docstring overstates the guarantee a reader relies on |

## Steps to Reproduce

> **Read the Triage section below first.** Two of the steps here assert conditions that
> have since LAPSED and were confirmed lapsed by execution on 2026-08-15: `code.md:17` no
> longer ends in a full stop, and `pre-commit`'s `run()` stashes `$out` on both paths
> (fixed under BG0239). They are left unedited because a reproduction is a record of what
> was observed when the bug was filed; the Triage table is the record of what is true now,
> and an independent review found a reader could follow these steps and re-open the bug on
> a premise the artefact itself already refutes.

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
