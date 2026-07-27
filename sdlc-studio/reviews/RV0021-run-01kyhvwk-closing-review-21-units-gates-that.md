# RV-0021: RUN-01KYHVWK closing review: 21 units, gates that now fail loud

> **Date:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1

## Scope

RUN-01KYHVWK: 21 units, 70 points - 16 bugs from the 2026-07-27 adversarial audit (BG0302-BG0306,
BG0314-BG0317, BG0321-BG0326, BG0329) and the five stories of EP0166 (US0447-US0451, delivering
CR0425 and CR0426). Diff base c3735565..39a31028.

Sprint Goal: every gate the audit showed silently standing down or silently passing fails loud, and
no terminal artefact carries a claim its own verifier contradicts.

Delivered across eight file-disjoint lanes derived from the planner's own `--export-lanes`
partition, red-first per unit. Review is independent of every author: three adversarial reviewers
over disjoint slices of the diff (parser and gate, the silent-success modules, the persona and
validate work), none of which wrote any of it, plus the operator as reviewer of record.

## Deterministic evidence

- Skill suite 4605 tests, tools suite 369: both green. Two errors surfaced on the first full run
  and were cross-lane, not per-lane: BG0316's new Done gate correctly refused two long-standing
  fixtures built on the old permissive behaviour. Repaired by substituting an honestly-declared
  manual verifier for the stripped one, which is the distinction BG0316 exists to draw.
- All 12 executable acceptance criteria across US0447-US0451 pass under `verify_ac`.
- `reconcile detect`: zero drift. `validate check`: zero errors.
- `review_prep`: zero required legs absent; **personas unused=0**, where the RV0010 condition that
  motivated CR0425 was that no registry persona was consulted at all.
- Installed copy re-synced (25 files); `forward-port --check` clean.
- Engagement floor refused the batch for carrying no plan until each bug named the test proving it.

## Findings

Three independent reviewers over disjoint slices of the delivery returned **REJECT** with 10 major
and 9 minor findings. Five of the ten majors were in code the author wrote, not the delivery agents'.

**Majors, all repaired in c4b1aaea:**

1. `verify_ac.parse_story` - BG0305's fix was incomplete and the shell injection it exists to close
   was STILL LIVE. CommonMark requires a closing fence carry nothing but spaces; a line carrying an
   info string still released the block, so an illustrative Verify line beneath it became a live
   verifier. Demonstrated end to end by the reviewer. The bug stood at Fixed carrying a comment
   asserting the rule was CommonMark's.
2. `transition._acs_missing_evidence` - a bare acceptance criterion still reached Done once any
   `Verified:` marker was added, while the release lane counts it unspecified and refuses. The two
   gates disagreed about the same file, which is the defect BG0316 names, and a new test pinned it.
3. `gate._provenance` - ignored the blocking flag on provenance findings, so an unreadable artefact
   never blocked despite BG0323 marking it blocking.
4. `eval_run.cmd_report` - forbidden behaviours were absent from the ungraded sweep, so a scenario
   printed "gate pass" having graded none of them.
5. `sprint._drift_warning` - hardcoded one of two causes of an unverified drift check and offered a
   remedy that does not clear the other.
6-9. The author's placeholder baseline - `Path(None)` crashed past an OSError-only handler; the
   cache leaked across repo roots and froze a failed read as empty; matching on artefact id waived
   every future blank in a listed record; and both its tests SURVIVED the feature being patched out.
6. `validate._check_placeholders` - still carried the naive fence toggle that the same commit had
   replaced in `verify_ac.py`, three files away.

**Repair.** Fence tracking is now one shared CommonMark implementation (`sdlc_md.fence_step`) called
by both parsers, rather than two local rules that disagreed. The transition gate is reordered with a
differential test asserting both lanes reach one verdict on one file. The baseline records the
FINDING rather than the artefact, is keyed by resolved repo root, and its tests are mutation-proven:
disabling the waiver kills two, and reverting to artefact-level matching kills the one written for it.

**Residuals filed rather than absorbed:** BG0347 (31 terminal artefacts with unfilled scaffolds,
12 of them bugs recording no symptom, steps or fix), BG0348 (the all-skipped hole survives for
unittest, jest, vitest and go - unittest is this repository's own default runner), BG0349 (four
modules still carry the naive fence toggle).

**Minors cleared in the repair:** six CHANGELOG fragments written, and two documentation claims that
BG0316 had falsified corrected - `reference-scripts-create.md` was telling consuming projects a gate
could not refuse them, immediately before it did.

## Verdict

**APPROVE**, at the third asking.

Two independent adversarial rounds both returned **REJECT**. Round one found 10 major and 9 minor
findings over the delivery; round two ruled 9 of those 10 CLOSED by mutation and refused the tenth,
because the repair had been silently reverted by a later unrelated commit - caught only by diffing
the claim against HEAD rather than against the commit that made it. Round two also found that three
repairs shipped with no regression coverage at all: reverting the provenance lane survived all 296
gate tests, and restoring the naive fence toggle survived the entire 4,322-test suite.

All of it is now closed. The reverted repair is restored, and the three unpinned ones carry
regression tests that are mutation-checked in both directions: restoring each defect kills exactly
its own tests, and all six pass with the code restored. Both suites green (4,624 and 370), gate
green, drift zero, installed copy in sync, and every executable acceptance criterion on the five
stories passes under `verify_ac`.

The honest summary of this sprint is that its delivery was not trustworthy and its review was. The
headline defect - a fenced illustration becoming a live shell verifier - was reported Fixed while it
was still reproducible, and the author's own contribution to the repair was the weakest code in the
batch, defended by two tests that survived the feature being deleted. Neither would have been caught
by the suite, the gate, or the author. Both were caught by readers who did not write it.

Signed off by Darren Benson as reviewer of record, 2026-07-27, after the independent rounds and
their repairs.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
