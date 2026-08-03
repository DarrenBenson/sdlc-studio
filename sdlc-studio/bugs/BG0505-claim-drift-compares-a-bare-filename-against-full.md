# BG0505: claim-drift compares a bare filename against full repo paths, so any Verify line naming a test by basename is a guaranteed false positive

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** tools/check_spec_claims.py, tools/tests/test_check_spec_claims.py
> **Verification depth:** functional
> **Evidence:** Reported by the pre-commit CLAIM-DRIFT lane on 2026-08-03 against the BG0504 commit; contradicted by `git diff --cached --stat` in the same working tree, which showed the file changed by 76 lines. Mechanism read from tools/check_spec_claims.py:563-606.
> **Created:** 2026-08-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`ticked_over_untouched` extracts surfaces from a criterion's Verify line with `_SURFACE_RE = ([\w./-]+\.(?:py|sh|md|ya?ml|json|ts|js))`, which matches an unqualified filename as readily as a path, and then tests `any(s in touched for s in found)` where `touched` holds repo-relative paths from `_diff_files`. A basename can never be a member of that set, so the check reports the criterion as ticked over an untouched surface whatever the diff contains.

The form that triggers it is the natural one. A unittest Verify line is written `python3 -m unittest discover -s tools/tests -p "test_epic_index_derived.py"`, because `-p` takes a pattern and not a path. That is the shipped invocation, so a correctly written criterion is the one this lane refuses.

Hit live: BG0504's AC3 was reported as `ticks ... while this diff does not touch test_epic_index_derived.py` in a diff whose `--stat` showed 76 changed lines in `tools/tests/test_epic_index_derived.py`.

## Steps to Reproduce

Stage a diff that modifies `tools/tests/test_epic_index_derived.py` alongside a bug artefact whose ticked criterion carries `- **Verify:** python3 -m unittest discover -s tools/tests -p "test_epic_index_derived.py"`. Commit: the pre-commit CLAIM-DRIFT lane reports the criterion as ticked over an untouched surface. Add the directory prefix to the Verify line and the finding disappears, with no other change.

## Proposed Fix

Match a bare name against the basename of each touched path, keeping the exact-path comparison for anything carrying a separator so a same-named file in another directory is not silently accepted as the same surface. A test for each direction: a basename-only Verify over a changed file must NOT be reported, and a basename that matches nothing in the diff still must be.

## Acceptance Criteria

- [x] **AC1: a ticked criterion whose Verify line names a changed file by basename alone is not reported.**
  - **Verify:** `test_a_bare_filename_naming_a_changed_file_is_not_flagged`, driving the exact shipped form `unittest discover -s tools/tests -p "test_touched.py"`
  - **Verified:** yes (2026-08-03)

- [x] **AC2: a basename matching no file in the diff is still reported, so the widening does not switch the lane off.**
  - **Verify:** `test_a_bare_filename_matching_nothing_in_the_diff_is_still_flagged`
  - **Verified:** yes (2026-08-03)

- [x] **AC3: a path-qualified name still compares by path, so `scripts/gate.py` is never satisfied by a change to `tools/gate.py`.**
  - **Verify:** `test_a_path_qualified_name_still_compares_by_path`
  - **Verified:** yes (2026-08-03) - the looseness is confined to the form carrying no directory to be wrong about

## Verification evidence

Functional. All 41 tests in `tools/tests/test_check_spec_claims.py` pass. The mutant - reverting
`_names_a_touched_file` to `any(s in touched for s in surfaces)`, the shipped behaviour this bug
describes - was executed with `__pycache__` purged under `python3 -B` and killed by AC1's test;
the source was restored and re-run green.

Two further mutants are named in the tests' own docstrings rather than executed, because each is
killed by a criterion above: returning `True` for every bare name (killed by AC2) and dropping the
`"/" in s` branch (killed by AC3).

## Impact

The lane ships advisory expressly so its yield can be measured before it is allowed to block, and AGENTS.md records that it earns its place on a number rather than on assertion. A systematic false positive on the commonest way to name a Python test corrupts exactly that number, upward. It also trains readers to skim CLAIM-DRIFT output, which is the failure mode an advisory lane can least afford.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-03 | sdlc-studio | Filed |
