# BG0241: A test spec with no AC Coverage Matrix at all reports clean and exits 0

> **Status:** Fixed
> **Verification depth:** functional - reproduced first, the two states printing byte-identical output (`ts-check: 0 finding(s) in <name>`, exit 0) before any edit; the migration cost was counted across every sdlc-studio workspace on this machine BEFORE the default changed (0 of 2 specs here, 30 of 178 across 11 repos); 8 of 12 new tests RED first; 9 hand-mutants, one SURVIVED and drove a stronger test
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Found and deliberately left in scope-declined state during BG0229, which fixed the adjacent case (a MISSING spec file read as an empty one and reported a clean matrix). The same vacuity family survives one step further in: a spec that is present, readable and valid UTF-8, but contains no AC Coverage Matrix section at all, still yields zero matrix rows and reports clean with exit 0. Absence of the section is indistinguishable from a section with nothing outstanding, which is the same defect BG0229 named - silence read as assertion integrity. Declined inside BG0229 because fixing it changes epic-ts semantics repo-wide, which is not a change to make mid-sprint on the way past; it earns its own unit, its own decision about what a spec with no matrix MEANS, and its own sweep of the specs that would newly fail.

## Acceptance Criteria

- [x] **AC1:** A spec that is present and readable but carries no AC Coverage Matrix reports a finding and exits 1, distinct from a complete matrix at 0 and an absent file at 2 (BG0229), so the three states are told apart by exit code alone.
      **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_verify_ac.py
- [x] **AC2:** A matrix heading with no rows is also a finding, so the check cannot be silenced by pasting two lines that assert nothing.
      **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_verify_ac.py
- [x] **AC3:** Prose merely naming the section is not accepted as a heading, so the classification cannot be satisfied by mentioning the matrix in a sentence.
      **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_verify_ac.py

## Steps to Reproduce

1. Take any test-spec file that is present and readable but has no AC Coverage Matrix section. 2. Run `verify_ac.py` ts-check against it. 3. Observe a clean report and exit 0, identical to the output for a spec whose matrix is complete. The two states are not distinguishable from the command's output or its exit code.

## Proposed Fix

Decide first what a spec with no matrix means - not yet written, deliberately not applicable, or malformed - because the three want different verdicts and only one of them is clean. Then make the absent-section case report distinctly from the complete-matrix case, the way BG0229 made the absent-FILE case exit 2 rather than 0. Before changing the default, sweep the existing specs to count how many would newly report, so the change lands as a known cost rather than a surprise red gate. Note the related guard already shipped: a vacuous verifier is refused per runner family, and a runner that ran nothing proves nothing whatever its exit code (L-0165).

## Resolution

Reproduced first. A present, readable spec with no matrix printed
`ts-check: 0 finding(s) in TS0001-no-matrix.md` with exit 0, and a spec with a complete matrix
printed the same line but for the file name. The two were byte-identical, which is the whole
complaint.

**The decision, taken before the code.** A spec with no matrix means NOT YET WRITTEN, and is
a finding. Of the three readings, only "deliberately not applicable" is clean, and a
deliberate exemption is a decision somebody made: nothing that is simply absent can evidence
a decision, so an exemption has to be written where a reader can see it and cannot be
inferred from silence. "Malformed" and "not yet written" both want work done, so both are
findings; they get DIFFERENT messages, because the repair differs (fix the columns, versus
write the matrix) and the file cannot tell the author which. No silence-shaped opt-out marker
was invented here: a new spec syntax needs documenting, and this unit may not touch the
reference files.

**The migration cost, counted before the default moved.** In this repo, 0 specs newly report:
both test-specs carry a matrix (TS0001 already had 28 findings before this change and still
has 28; TS0002 was clean and stays clean). Swept wider, across all 11 sdlc-studio workspaces
on this machine: 30 of 178 specs (17%) would newly report, none of which were failing for
another reason already, concentrated in four projects (10 in one, 9 in another, 7, and 4).
Seven projects, including this one, see no change at all. The gate is not turned red
unannounced here, and the repair in a consuming project is mechanical rather than editorial:
`verify_ac.py scaffold-matrix --epic EPxxxx --out <spec>` already emits a matrix pre-filled
with one row per AC across the epic's stories, leaving only Test Cases and Status to map.

`ts_check` now counts the matrix TABLES it found and the AC ROWS it read out of them, and
reports when either is zero. Absent is kept apart from the older refusals, because the
callers differ: an absent FILE is still a broken invocation (`FileNotFoundError` -> exit 2,
BG0229's behaviour, re-pinned here); a present spec with no matrix is a CONTENT finding on
exit 1, alongside an unmapped row. The empty-table case is covered with the absent-section
one deliberately - if a header with no rows under it stayed clean, the new finding could be
silenced by pasting two lines that assert nothing, which is the same vacuity wearing a hat.
`epic-ts` FAILs for an epic whose only spec asserts no coverage; that is the semantics change
the bug asked for and it is pinned directly.

Pinned by `TsCheckAbsentMatrixTests` in `tests/test_verify_ac.py`, 12 cases. The sharpest
compares the two commands' real OUTPUT rather than asserting a wording nobody re-runs, since
identical output was the defect. 8 of the 12 were RED first; one
(`test_the_missing_section_does_not_borrow_the_broken_invocation_exit`) cannot be red before
the fix by construction - it guards the fix from over-reaching to exit 2 and is only useful
beside the exit-1 assertion.

Mutation-proven by hand (bytecode purged, `python3 -B`, each patch asserted to have changed
the file on disk), 9 mutants. Killed: the absent-matrix finding dropped; the empty-matrix
finding dropped; malformed and unwritten reporting identically; the heading pattern widened
so a prose mention reads as a heading; AC rows never counted; the `elif` opened to an `if`
so one absent matrix reports twice; BG0229's absent-FILE refusal dropped.

One mutant SURVIVED first time and is worth recording: counting ANY table as a matrix. The
test asserting a Revision History is not coverage checked only that SOMETHING was reported,
and the mis-count still reports something - the wrong finding, telling the author to fix the
columns of a table that is not the matrix. The test now pins the CLASSIFICATION, by requiring
the same message a spec with no tables at all produces, and the mutant is killed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
| 2026-07-21 | claude | Fixed - an absent or empty matrix is a content finding on exit 1, distinct from the absent-FILE refusal on 2 and from a complete matrix on 0, with malformed named apart from unwritten; migration cost counted first (0 of 2 here, 30 of 178 across 11 workspaces); 12 tests, 8 RED first, 9 mutants with one survivor found and fixed |
