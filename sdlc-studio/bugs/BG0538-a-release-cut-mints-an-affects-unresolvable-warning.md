# BG0538: a release cut mints an affects-unresolvable warning for every unit that declared its own changelog fragment, because compose deletes the file the unit named

> **Status:** Fixed
> **Verification depth:** functional (executed: unresolvable_affects over a consumed changelog.d fragment returns [] where it reported a fictional file, with a genuinely missing path elsewhere still reported as the control; mutation: 2 declared mutants, anchors asserted unique, bytecode purged, python3 -B, both KILLED, restore byte-exact)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Evidence:** RUN-01KZCAJX, 2026-08-07, after the v5.0.0 changelog cut consumed 298 fragments. `npm run lint:warning-ratchet` refused with nine unrecorded instances, every one a `changelog.d/*.md` path. Mutant `delete the _is_consumed_fragment filter` applied and shown to kill both new tests; restored byte-identical.
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The repo asks every behaviour change to ship a `changelog.d/<UNIT-ID>.md` fragment in the same commit as its code, and units that comply often declare that fragment under `Affects`. `changelog.py compose --apply` then folds each fragment into CHANGELOG.md and DELETES it.

`validate`'s `affects-unresolvable` rule fires on a terminal unit whose `Affects` names a path not on disk, and its message states the reasoning: the unit is Done, so the file it declared should exist by now - a typo, or a claim about code that never landed. Neither is true of a consumed fragment. The file is absent because the toolchain removed it on purpose.

So a release cut converts compliance into permanent warnings, and because these are ratcheted, the tolerated set can only shrink - the new instances are refused outright and block every subsequent commit. The v5.0.0 cut produced nine at once: BG0471, BG0472, BG0480, BG0487 (twice), US0470, US0471, US0472 and US0473. Every one of them had done the right thing.

## Steps to Reproduce

1. Deliver a unit that ships `changelog.d/<ID>.md` and names it in `Affects`. 2. Move the unit to Done. 3. Run `changelog.py compose --apply` as a release cut does. 4. Run `npm run lint:warning-ratchet`. Nine instances the baseline does not record, and the ratchet refuses. The warning names a file the previous command deleted by design.

## Acceptance Criteria

- [x] **AC1** Given a unit declaring its own `changelog.d/<ID>.md` fragment under `Affects`, when the fragment has been consumed by a release cut, then the path is NOT reported unresolvable - complying with the changelog rule must not mint a warning for complying.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py -k a_consumed_changelog_fragment_is_not_fictional
- [x] **AC2** Given a genuinely missing path outside `changelog.d/`, when the same check runs, then it is still reported - the exemption is one directory, not a hole.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py -k a_missing_path_elsewhere_is_still_reported

## Proposed Fix

Exempt the `changelog.d/` directory from the unresolvable half of the rule. Keyed on the DIRECTORY rather than on a `<ID>.md` name shape: what makes a fragment transient is where it sits, not what it is called, and a name-shaped check would silently stop covering a fragment named any other way.

The undeclared half is untouched, and a real missing path sitting beside a fragment is still reported - that control matters, because an exemption that swallows the typo next to it is worse than the warning.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in file_finding.py `unresolvable_affects`, drop the `_is_transient_path` guard so a consumed fragment reads fictional | Given a unit declaring its own `changelog.d/<ID>.md` fragment under `Affects`, when the fragment has been consumed by a release cut, then the path is NOT reported unresolvable - complying with the changelog rule must not mint a warning for complying. |
| AC2 | in file_finding.py `_is_transient_path`, return True always so every missing path is excused | Given a genuinely missing path outside `changelog.d/`, when the same check runs, then it is still reported - the exemption is one directory, not a hole. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Filed |
