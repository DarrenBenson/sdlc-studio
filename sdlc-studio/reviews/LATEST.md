# Reviews - LATEST (anchor)

> Derived from **RUN-01KY2K5R** (the open-bug batch, 2026-07-21, RETRO-0064).
> Supersedes the RETRO-0063 picture. Full detail lives in RETRO-0064; this is the anchor.

## Where the pipeline is (2026-07-21)

**RUN-01KY2K5R delivered 10/10 units, 21 points, one wave** - the entire open-bug backlog. The
closing review REJECTED at round 1 on two MAJORs; both were repaired and the same reviewer
re-executed its own reproductions to APPROVE at round 2.

Sprint Goal: *every number this project publishes is either measured or refused, and the test
suite cannot reach the repository that runs it.*

## What shipped

Seven of the ten were one defect class - a number or gate reporting something never measured.

- **BG0236** - the close captured the harness meter's ABSOLUTE reading, cumulative per session, so
  a second sprint in one session booked the first's spend (472,691 tokens/point against a ~25,000
  rate, hand-blanked twice). `open_run` stamps a baseline, the close reports the delta, and a
  baseline-less run says **not-attributable** with no fallback.
- **BG0238** - mutation evidence was one blob, last-write-wins, stale-keyed on a repo-wide
  `git_rev`, so per-unit runs never reached the close. Now a bounded ledger keyed on each target's
  content hash, with the lane judging **coverage of the changed surface**.
- **BG0239** - the budget recorded a total whenever the suite lane was INVOKED. Now gated on a
  loader-error fact plus a test-count floor, deliberately **not** on duration.
- **BG0230** - a fixture's git call could be redirected at the parent repo by the ambient
  environment. Variables dropped AND discovery fenced, plus a sweep so a fifth scrub-list copy
  cannot arrive unpinned. Residual hole declared, not hidden: BG0242.
- **BG0237 / BG0229 / BG0228 / BG0227 / BG0233 / BG0235** - installed-copy failures made hermetic
  and the dev-repo rule single-sourced; a missing spec refused not read as empty; `repo_map`
  anchored on its root; three pin-only units closing surviving mutants.

## The review REJECTED, and both MAJORs were the sprint's own sin

For the **fourth consecutive sprint** the surviving defect was prose asserting a property the code
did not have (L-0146, L-0173).

1. **The mutation coverage lane counted files nothing had mutated.** The gate overlaid the report's
   `target_hashes` - written for every named target before any verdict exists - on top of the
   ledger that correctly applies the verdict rule. A REFUSED run printed "nothing was proven" and
   "covers 1/1" in one sentence. **A bug meant to stop unmeasured numbers was publishing one.** The
   deleted `if not refused` guard had been removed on evidence from the ledger, never from the
   report the gate actually reads.
2. **`session_tokens` raised on a malformed transcript record**, so `sprint plan --write` minted no
   run at all - while its docstring promised "never raises". The counter-example sat 100 lines up.

## Evidence

**75 mutants in the build, 5 SURVIVED first time**, each driving a second fix; 12 more across
repair and re-verification. Every survivor read as coverage while pinning nothing - and the
**unreachable-guard trap (L-0159) was hit three times by three authors** (BG0237's `_report()`
guard, BG0236's `_session_baseline` backstop, BG0238's `recorded is None` clause). All now pinned.

Round 2 was verified by the **same** reviewer re-running its own reproductions: both MAJOR
fixtures re-executed, the fallback claim rebuilt across four cases, six transcript shapes swept.

**Dogfood:** this run predates BG0236's fix, carries no baseline, and reports **not-attributable**
at its own close. No baseline was retrofitted.

## Next steps

- **CR0384** (High) - filing a finding passes fields through a shell, so reproduction steps get
  EXECUTED: it deleted two commands from BG0240 and ran `git commit -a` twice, both gate-blocked.
- **BG0244** (High) - the velocity row wrote `Actual (tokens) = 0` when NO unit was rated - an
  absence published as a measurement, hand-corrected for a third sprint.
- **BG0245** (High) - the mutation ledger is written only by `mutation.py` while the practice is
  hand-applied mutants, so the lane reads 0/N after a sprint that followed policy: 75 mutants
  applied here, coverage reported 0/4. BG0238 built the recorder, not the recording.
- **BG0242** (High) - 35 bare `subprocess` git calls bypass BG0230's fix: bounded, not closed.
- **BG0240, BG0241, BG0243, CR0382, CR0383, CR0385** open. **RFC0048 D2** authorised test
  retirement on measured kill-yield, SEQUENCED behind CR0377 and BG0238.
- **CR0319** is the release cut, freeze expired. **RFC0050** unbuilt; its risk lens subsumes
  RFC0049 option B - do not build both.

## Lessons

A rule enforced in the producer is not enforced in the consumer. Deleting a guard needs evidence
from the surface it protects. Building the recorder is not recording. Full set: RETRO-0064.
