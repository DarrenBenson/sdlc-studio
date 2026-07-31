# BG0456: A ruling verb short-circuits the destination check, so a tick citing an artefact nothing holds is accepted - and the corpus-read pin is inert because its fixture never scales

> **Status:** Fixed
> **Verification depth:** functional (each half verified by applying its own mutant, `assert count(anchor)==1`, `__pycache__` purged, `python3 -B`, restored byte-identical: the ruling-verb bypass and the dangling-decision branch both KILLED; the absent-table carve-out SURVIVED a first attempt whose test used a ruling verb - the verb settled the item before the branch was reached - and was KILLED once the test dropped it)
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py, sdlc-studio/stories/US0532-the-corpus-read-is-measured-by-a-test.md, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py
> **Evidence:** Independent adversarial review of RUN-01KYTKA1 tranche C (engineering seat, isolated worktree). US0465=REJECT, US0532=REJECT, with executed reproductions for both.
> **Created:** 2026-07-31
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Two guards reporting green over something they never checked, in work already delivered and standing at Review.

First: `unresolved_questions` tested `_RULING_RE.search(item)` BEFORE either destination check, so any item carrying a ruling verb was accepted whatever it cited. `- [x] deferred, resolved by BG9999` passed while the identical citation without the verb was refused, which is precisely the tick-pointing-at-nothing the helper's own docstring promises cannot happen. The same short-circuit made `_decision_cited`'s existence check unreachable for the natural `ruled by D9999` phrasing - a written check standing beside the defect it was written to prevent, dead for its whole life. The verb branch also sat above the unchecked-box test, so an OPEN box wearing a ruling verb was accepted too.

Second: US0532's pin claims a corpus read cannot silently regress to per-unit. Its fixture performed a constant six lookups regardless of unit count, so an uncached run read 6xN and a cached run read N - both linear. Doubling the corpus therefore doubled BOTH and the asserted ratio sat at 2.0 whether the cache existed or not.

## Steps to Reproduce

Ruling-verb escape, before the fix:

```text
unresolved_questions('## Open Questions\n\n- [x] deferred, resolved by BG9999\n', '.') -> []
```

Accepted, with no BG9999 anywhere in the workspace. Four shapes escaped: `resolved by`, `ruled by`, `settled in` and `decided:`, ticked or unticked.

Inert perf pin, measured by the reviewer and reproduced by the author:

```text
corpus_cache live     : reads(20)=42  reads(40)=82   ratio=1.95  PASS
corpus_cache neutered : reads(20)=378 reads(40)=738  ratio=1.95  PASS
```

A ninefold loss of the whole optimisation, an identical ratio, and a green test.

## Proposed Fix

One destination check, consulted by BOTH routes out of an open question, so a ruling and a follow-up cannot be held to different standards. A ruling that names a destination is held to it; a free-text ruling naming none is still accepted, because that is the heading route written in place. Separate an ABSENT decisions table from a table that exists and does not hold the cited id - a project keeping no decision log must not have every citation refused, which would be a guard manufacturing work.

For the pin: scale the fixture's lookups with the corpus so the uncached case is quadratic and the cached case linear. The ceiling then sits on a real boundary rather than between two readings of the same number.

## Acceptance Criteria

### AC1: a ruling verb no longer bypasses the destination it names

- **Given** an open-question item carrying a ruling verb and citing an artefact or decision row that resolves to nothing
- **When** a terminal transition is attempted
- **Then** it is refused, ticked or unticked, while a free-text ruling naming no destination and a citation of a decision row that exists are both still accepted
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::OpenQuestionsGateTests::test_a_ruling_VERB_does_not_buy_an_exemption_from_the_id_it_cites
- **Verified:** yes (2026-07-31)

### AC2: a dangling decision citation is refused, and an absent table is not a dangling one

- **Given** a decisions table that exists and does not hold the cited row, and separately a project that keeps no decisions table at all
- **When** the same item is judged in each
- **Then** the first is refused and the second accepted, and the carve-out is pinned by an item carrying NO ruling verb - written with one, the verb settles the item first and the test passes whether the carve-out exists or not, which a mutation run caught it doing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::OpenQuestionsGateTests::test_a_project_keeping_NO_decisions_table_is_not_held_to_one
- **Verified:** yes (2026-07-31)

### AC3: the sweep fixture issues a lookup per unit, which is what makes the ratio pin mean anything

- **Given** the sweep the corpus-read pin measures
- **When** its lookups are counted over corpora of 20 and 40 units
- **Then** it issues 20 and 40, because a ratio test cannot report its own inertness: with a fixed lookup count both the cached and the uncached sweep are linear, the ratio is 2.0 either way, and the assertion holds over a total loss of the cache. The scaling is a different fact from the ratio and needs its own assertion rather than a share of one - with the fixture scaled, neutering `corpus_cache` moves the measured ratio from 1.95 to 3.90 and reddens US0532 AC1
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::CorpusReadOnceTests::test_the_sweep_fixture_ISSUES_a_lookup_per_unit
- **Verified:** yes (2026-07-31)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-31 | Claude Opus 5 | Filed |
