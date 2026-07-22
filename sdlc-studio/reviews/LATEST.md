# Reviews - LATEST (anchor)

> Derived from **RUN-01KY3MFX** (2026-07-22). Supersedes the RETRO-0065 picture.
> The run is BUILT, REVIEWED TWICE and REPAIRED TWICE. It is NOT closed: no retro, no
> sign-off, no velocity row. Full detail lives in the review record; this is the anchor.

## Where the pipeline is (2026-07-22)

**RUN-01KY3MFX delivered 32 units, 100 points** - 9 bugs plus 23 stories decomposed from the
ten High-priority requests, in seven file-disjoint lanes. Goal: *every open bug and every
High-priority request built, verified and independently reviewed.*

**It stops one step short by design.** `review.two_role_after: 192` means every story here
reaches Done only with a reviewer-of-record sign-off the authoring session is refused. The
stories sit at **Review**. See RFC0051.

## What shipped

- **Measurement** - the rate reads the velocity record and REFUSES across models (BG0248,
  US0290); the velocity row is owed at close, 24 rows backfilled with blanks not zeroes
  (US0288, US0289, BG0249); the capture names main-thread measured and delegated supplied, the
  sum a lower bound (BG0252); the forecast declares it prices the BUILD (BG0254); the mutation
  gate logs cost against yield (US0301, US0302, US0309).
- **Guards that reach** - collision files derive from Verify lines and a contradicted `Affects`
  is reported from ONE predicate shared by planner and validate (US0291, US0292);
  `quality.epic_requires_test_spec` is read by the code four documents said read it (BG0250);
  the floor sees the violation its own commit creates (BG0251); a declared rewrite window
  refuses a commit staging what it claims (US0307, US0308, US0310); run ids are collision
  checked (BG0253).
- **Onboarding** - migrate seeds a missing AGENTS.md (US0293, US0294); the hygiene check
  verifies the working model, not just pointers (US0295, US0296); init no longer ships a
  literal placeholder (BG0255); a non-shell filing path (US0305, US0306); a `test` audit lens
  (US0303, US0304); the seats review the Sprint Goal (US0297, US0298); a sprint stops only when
  nothing can proceed (US0299, US0300).

## What the reviews found

**Round 1: REJECT from three independent instances. 11 MAJOR.** The two worst were structural:
US0307 and US0308 shipped CONTRADICTING each other (the gate's window lane froze every commit
while the hook printed that staging was merely scoped, hidden because the fixture stubbed the
gate out), and US0310's four `grep` verifiers all passed on prose asserting the opposite of
their criteria - so the published "84 ACs verified" was four higher than the evidence supported.

**Round 2: REJECT. Of round 1's eleven repairs, 5 CLOSED, 3 OVER-CLAIMED, 3 MOVED.** All three
over-claims were the same species - the code improved and the prose describing it got ahead of
the code, the surviving MAJOR in seven consecutive closing reviews. One was the author's own:
the engagement floor's unreadable-index refusal was reached by NO test, its guard mutated to
`if False:` left 3,891 tests green, and BG0251's Resolution called it mutation-proven.

**The standing lesson, hit three times: a repair can MASK the defect beside it.** Un-stubbing
the gate hid two hook mutants; removing the hook's traversal branch leaves the end-to-end test
green because the fixture's gate stub refuses the record for its own reason. Only isolation
tests kill them. Recorded as a property of the fixture in US0308.

## Evidence

3,927 skill tests + 312 tool tests green. Drift 0, conformance 0 non-conformant, floor 0
violations, no rewrite window open. ~220 hand-applied mutants across build and both repair
rounds; 13 survived first time and every one drove a change rather than a re-run. Installed copy
forward-ported and verified.

## Next steps

- **Round 3 review has NOT been run.** The ceiling is 3 (`review.max_rounds`). Round 2's repair
  is unreviewed.
- **Sign-off is owed and is the operator's.** `sprint close --retro <id> --apply-signoff
  --principal "..."`. RFC0051 records why an agent cannot honestly supply it.
- **Owed at close:** a retro, a velocity row (US0288's own gate will demand it), and the
  delegated-token figure BG0252 needs supplied by hand.
- **Filed during the run:** BG0255, BG0256, CR0389, CR0390, RFC0051, D0051-D0053.
- **CR0319** is the 5.0.0 release cut, still outstanding.

## Lessons

A library test is not a lane test. A repair can mask the defect beside it. Prose that justifies
code is the least-reviewed code in the repo, for the seventh sprint running.
