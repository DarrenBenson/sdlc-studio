# BG0289: give the 5 scripts with no --root surface one, and reconcile the census (BG0282 slice 3)

> **Status:** Fixed
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/, sdlc-studio/reviews/root-census.md
> **Verification depth:** functional (census summary counts parsed and held to the measurement, stale-not-false waiver removed so a row fails whichever way it disagrees; the title's premise was tested and did not survive - none of the 5 should take a --root, recorded on the bug)
> **Severity:** Low
> **Points:** 2

## Summary

Slice 3 of [[BG0282]]: the 5 scripts the census records `non-root`, and the census itself.

**The title's premise did not survive the investigation, and the record says so rather than
quietly delivering something else.** Each of the 5 was read at delivery, and none should be
given a `--root`:

- `carry_forward.py` has no command line at all. A `--root` would be a surface with nothing
  behind it; its caller passes the resolved root already.
- `triage_noise.py` and `triage_sampling.py` are the same case with a `--help` stub bolted on
  so `disclosure` and a human can learn their role. They dispatch to no verbs.
- `plan.py` operates on the operator's `~/.claude/plans/` tree through `--plans-dir`. That tree
  sits outside any project, so a project root is meaningless to it.
- `pvd.py` takes a `--master` and a `--target` repo. There is no single project root to anchor.

What was genuinely broken was the record. The census confessed two holes in its own prose and
neither was fixed: the summary counts "are never parsed, so the counts were unverified by
construction", and the guard "waives a row that RECORDS `unanchored` while MEASURING `anchored`
as stale-not-false". Together those let the block claim 5 anchored / 59 unanchored while the
family measured 10 / 54, with a green suite. Two of the five `non-root` reasons were also
false: `triage_noise.py` and `triage_sampling.py` are recorded as having "no CLI surface" while
both define `main()`.

## Steps to Reproduce

1. Read the counts block of `sdlc-studio/reviews/root-census.md`.
2. Re-measure the family: `python3 -c "import sys; sys.path.insert(0,
   '.claude/skills/sdlc-studio/scripts/tests'); import test_root_census as t;
   from collections import Counter; print(Counter(t.measure().values()))"`.
3. Observe the two disagree, and that `python3 -m unittest tests.test_root_census` is green
   anyway.
4. Read the `triage_noise.py` row, then `grep -n "def main" triage_noise.py`.

## Proposed Fix

Do not add a `--root` anywhere. Close the two holes in the guard instead, so the record cannot
drift from the measurement again:

1. Parse the summary counts and hold them to the measurement.
2. Drop the stale-not-false waiver: hold every row to the measurement in both directions.
3. Hold each `non-root` reason to the code, so "deliberately out of scope" cannot become a
   place to park a script nobody wants to classify.

Then re-measure and rewrite the record.

## Acceptance Criteria

### AC1: the summary counts are the measured counts

- **Given** the counts block in `sdlc-studio/reviews/root-census.md`
- **When** the guard re-measures the family
- **Then** each classification's count, and the total, match what was measured - a count nobody
  reads is a claim nobody checks
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_root_census.RootCensusTests.test_the_summary_counts_are_the_measured_counts
- **Verified:** yes (2026-07-24)

### AC2: a stale row fails instead of being waived

- **Given** a row whose classification disagrees with the measurement in EITHER direction
- **When** the guard runs
- **Then** it fails - the waiver that let five anchored scripts keep an `unanchored` row is gone
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_root_census.RootCensusTests.test_every_root_declaring_script_is_classified_with_a_reason
- **Verified:** yes (2026-07-24)

### AC3: each non-root reason is held to the code

- **Given** a row recorded `non-root`
- **When** the guard reads the script it names
- **Then** the stated reason is true of the source: a claim of no CLI means no `main`, a claim
  of a `--help` stub means a `main` that dispatches to nothing, and a named path option must be
  one the script declares
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_root_census.RootCensusTests.test_a_non_root_reason_is_true_of_the_code
- **Verified:** yes (2026-07-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Groomed from the skeleton; the premise was refuted and the record says so |
