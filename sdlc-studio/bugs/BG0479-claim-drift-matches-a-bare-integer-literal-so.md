# BG0479: claim-drift matches a bare integer literal, so unrelated changelog fragments are reported against any diff that changes a small number

> **Status:** Fixed
> **Verification depth:** functional (corpus replay over 40 commits, before 215/135-empty vs after 74/0-empty; four tests pin both guards with positive controls)
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Provenance:** agent
> **Raised-by:** Claude Opus 5; human; v1
> **Affects:** tools/check_spec_claims.py, tools/tests/test_precommit_claim_drift.py
> **Severity:** High
> **Points:** 5

## Summary

The advisory claim-drift lane compares a diff's REPLACED literals against standing prose in
changelog.d/. Two faults compound, and together they make the lane's output overwhelmingly
noise. This bug was opened on the first and then enlarged by an independent QA seat's
replay, which found the second and the root cause common to both.

**The root cause.** `claim_drift` computes the replaced set as `old_nums - new_nums`. When a
hunk's added lines contain no integer at all, that set is the whole of `old_nums`, so every
integer on the removed side is treated as replaced and matched against all 181 changelog.d
fragments. Pure deletions therefore fire on `0`, and a hunk like `-DEFAULT_RETRIES = 2` /
`+DEFAULT_RETRIES = RETRY_LIMIT` fires on two unrelated fragments.

**Measured over the corpus, not one commit.** The independent QA seat replayed the lane
across the 40 commits ending at `3570c94a` and reported **235 findings, 12 of 40 commits
firing, and 191 (81%) carrying an empty code anchor**. A second replay taken here over the
same window measured **215 findings, 11 commits firing, 135 (63%) empty**. Both runs were
taken at the same HEAD, so the gap is the `changelog.d/` corpus `_standing_prose` reads,
which grew between them. The two numbers are recorded side by side rather than reconciled
into one, because neither was reproduced by the other.

Either way the shape is the same and the conclusion does not turn on which is right: the
majority of the lane's output prints as `CLAIM-DRIFT: <prose> says '...' while <file> in this
diff carries ''` - a report naming nothing the reader can act on. The premise was measured on
a single commit at delivery time; measured over forty it does not discriminate.

**Second fault, the one this bug was opened on.** Even where the anchor is non-empty, a bare
small integer is not a discriminating literal. Observed this run: a diff changing `if len(cells) == 6:` to `if len(cells) == 7:` in critic.py drew two reports, one against changelog.d/BG0467.md and one against changelog.d/US0458.md. Neither fragment is about critic.py, the verdict table, or column counts. Both were reported solely because their text contains the digit that was replaced. The lane's own output shows this: it quotes a sentence about the commit gate's test selection beside a column-count condition and asserts the two disagree.

This matters beyond noise. US0585 ships claim-drift as advisory specifically so its yield can be MEASURED before it is allowed to block, and `record_yield` writes those counts to retros/evidence/claim-drift-yield.json. Reports of this shape inflate the yield with findings that could never be actioned, so the number the blocking decision will rest on is currently measuring the wrong thing.

## Steps to Reproduce

Empty anchor (81% of the corpus yield):

1. Stage a hunk whose added lines contain no integer, e.g. `-DEFAULT_RETRIES = 2` to
   `+DEFAULT_RETRIES = RETRY_LIMIT`, or any pure deletion.
2. Run the claim-drift lane over that diff.
3. It reports against unrelated changelog fragments with an empty `carries ''` anchor.

Bare integer (the non-empty remainder):

1. Change any small integer literal in a tracked Python file, e.g. a `== 6` to `== 7`.
2. git add it and commit.
3. The lane reports CLAIM-DRIFT against changelog fragments whose only connection is
   containing that digit.

## Proposed Fix

Two changes, both needed, because either alone leaves most of the yield in place.

**Never emit a finding with an empty code anchor.** A report that cannot name the code it
objects to is not actionable by construction, and it is the majority of what the lane
currently produces. Where `old_nums - new_nums` returns the whole removed set because the added side
carries no integer, there is no replacement to reason about and the correct output is
nothing.

**Require a replaced literal to be discriminating.** Skip bare integers below some floor, or
require the prose match to carry a token from the changed symbol's context - the identifier,
the file stem, the surrounding condition - rather than the number alone.

Then re-run `record_yield` over the same corpus and compare. The point of the advisory
period is that the blocking decision rests on a measured number, and both faults mean the
number now on disk was measured with the noise included.

## Acceptance Criteria

### AC1: a finding never names an empty code anchor

- **Given** a hunk whose added lines carry no integer, so there is no replacement to reason about
- **When** the lane runs over it
- **Then** it emits no finding whose code anchor is empty, and a hunk that DOES carry a new value still fires
- **Verify:** pytest tools/tests/test_precommit_claim_drift.py::DiscriminationTests::test_a_finding_never_names_an_empty_code_anchor
- **Verified:** yes (2026-08-01)

### AC2: a shared digit alone is not a finding

- **Given** prose whose only tie to the changed code is the replaced digit
- **When** the lane runs over it
- **Then** nothing is reported, while prose naming the changed subject still is
- **Verify:** pytest tools/tests/test_precommit_claim_drift.py::DiscriminationTests::test_a_shared_digit_alone_is_not_a_finding
- **Verified:** yes (2026-08-01)

### AC3: the empty-anchor class is gone, not merely smaller

- **Given** the same 40-commit window replayed before and after the repair
- **When** the recorded arms are read
- **Then** the before arm records empty-anchor findings and the after arm records none, because a report that cannot name the code it objects to is not actionable by construction
- **Verify:** pytest tools/tests/test_claim_drift_replay.py::ReplayTests::test_the_after_arm_records_no_empty_anchors
- **Verified:** yes (2026-08-01)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | Claude Opus 5 | Created via `new` (deterministic) |
