# Reviews - LATEST (anchor)

> Derived from the sprint-close review of **RUN-01KY03GS** (bound the close review loop and
> clear the instruments close-debt, 2026-07-20, RETRO-0061). Supersedes the RETRO-0060 picture.

## Where the pipeline is (2026-07-20)

**RUN-01KY03GS is built, verified, reviewed and closing**: 13/13 units, 31 points - Phase 2
of the v5.0 plan (EP0085 / CR0358, bound the close review loop) plus the eight close-debt bugs
from the instruments sprint. The five stories were reviewed by an independent adversarial pass
(APPROVE, round 1, reviewer != author) - the first exercise of the round-counting machinery on
its own delivery - then countersigned by the operator as reviewer of record.

## What shipped

- **EP0085 / CR0358 (US0261-US0265)** - the close review is a bounded, priced, un-primed loop:
  rounds counted on the run state with a configurable ceiling (default 3) and a recorded
  override; a finding in the previous round's repair surface classified a repair regression by
  file AND line; escalation to revert / redesign / accept-and-file instead of another patch
  round; per-round token cost with an unmeasured round named not zeroed; and a reviewer brief
  that carries the probes to re-execute but not the verdict prose, round number or conclusion.
  US0265 narrowed CR0358's AC5 deliberately so the probe re-execution demand survives.
- **BG0217** - validate's placeholder warning uses the severity the counters count.
- **BG0220** - verify_ac resolves paths against the project root, on six surfaces.
- **BG0221** - refine --into merges epic criteria instead of duplicating the AC heading.
- **BG0222** - the suite lanes run in a git environment of their own.
- **BG0223** - a run stopped mid-flight can still take the bounded exit.
- **BG0224** - an explicit --tokens 0 clears a recorded actual.
- **BG0225** - the close-owed detector reads a Batch line's parenthesised units.
- **BG0226** - a dashed retro id no longer mints an invisible velocity row.

3396 tests green at every commit; 25/25 story ACs verified. Mutation over the sprint diff
(scoped to product files): 16 applied, 13 killed, 3 survived, all three verified real gaps and
filed. 16 of 3153 enumerated sampled - the rest recorded as un-checked, not clean.

## The CODE leg - one round

| Round | Findings | Outcome |
| --- | --- | --- |
| 1 | 2 test-completeness (both non-blocking, filed BG0235) | APPROVE |

The independent reviewer mutation-pinned every central claim, confirmed the one known
equivalent mutant is genuinely equivalent, and left the tree byte-identical. Its two findings
were that the ceiling literal is asserted symbolically and the priming classes only in
aggregate - real coverage gaps, no live defect.

## The incident this run survived

The BG0222 agent - fixing a bug about GIT_* environment leakage - pointed GIT_INDEX_FILE at
the live repo's index lock, and the suites emptied the index (1845 files staged deleted, a
fixture commit running against main). Recovered with git reset, no data lost. The filed
reproduction itself is the hazard. BG0230 (High) filed for the wider cause: the fixtures have
no containment of their own.

## Next steps

- **Freshness spine, top priority next sprint (operator-set):** BG0231 (a Done story stays
  green after its named test is deleted), BG0232 (ac_fingerprint has no test of its own),
  BG0234 (repo-wide-invariant ACs un-Done themselves as the repo grows). The mechanism that
  certifies a Done story is still true is currently unpinned in both directions.
- **RFC0048 option B next (operator-set):** attack the three heavy test files (test_gate.py is
  56s, 41% of the suite) - no coverage change, no policy decision. Then D6 sets the per-commit
  budget against the improved baseline, as this sprint resolved. The sprint ran ~2.4x baseline;
  ~23 min of it was the pre-commit suite across nine commits.
- **CR-0378** (never park the batch on one unit's decision) and **CR-0379** (log mutation yield
  and cost as a series) - both filed from this run's own process failures.
- **conformance.adopt_after is at 115** for US0112/US0115 only, expected to come back down when
  BG0234 lands. **CR0374** (surface the single-writer window a live mutation run holds) was hit
  twice this run and held by hand both times.
- Standing: **RFC0046** needs D1 closed or an override; **CR0319** is the release cut. Release
  freeze holds.

## Lessons this run paid for

L-0158 to L-0162 (RETRO-0061): a bug about environment pollution must never be reproduced next
to a live repo (assert the parent index hash unchanged); a guard unreachable through the public
path cannot be tested through it; scope a mutation run to product code with a scoped test
command; a -k filter is part of the harness and can silently exclude the tests you rely on; an
AC's freshness must cover whether its verifier still exists.
