# Reviews - LATEST (anchor)

> Derived from the close of **RUN-01KY0VNV** (the freshness spine certifies a Done story
> truthfully, 2026-07-21, RETRO-0062). Supersedes the RETRO-0061 picture.

## Where the pipeline is (2026-07-21)

**RUN-01KY0VNV is built, verified and closing**: 3/3 bugs, 8 points - the freshness-spine
cluster the operator prioritised. Bugs are terminal at Fixed, so no two-role sign-off applies;
each fix was mutation-checked per-unit during the build (8 mutants killed across the two code
changes), so the close carries its evidence without a separate diff-scoped pass.

## What shipped

- **BG0232** - `ac_fingerprint`, the mechanism that decides whether a green verify entry is
  still trusted, is pinned by its own test from both sides: stable across a Status change, a
  Revision History row and the machine-maintained Verified stamp; changes on a re-pointed
  verifier, a retitled AC, or an added/removed AC. Characterisation - the function was correct,
  nothing had tested it. A no-op mutant of it had survived the whole suite; now four mutants die.
- **BG0231** - an unresolved pytest verifier (a deleted `::node` exits 4, a stale `-k` pattern
  exits 5) is attributed **vacuous** with the "re-point the Verify line" remedy instead of
  misreported as a code failure. Scoped to pytest's no-collection codes so a shell verb's own
  nonzero exit stays a plain failure. The **trigger** half - re-verifying an already-Done story
  so a green cannot persist between closes - is split to **CR0380**, cost-sensitive and
  interacting with RFC0048.
- **BG0234** - two point-in-time-cleanup ACs (US0112 AC2, US0115 AC1) that asserted repo-wide
  invariants as executable checks are reclassified `manual` (verified at delivery). Their Given
  clauses name a snapshot, so the executable form was a category error that un-Doned the story
  on unrelated later growth. `conformance.adopt_after` went back to 82, no standing exemption.

3409 tests green.

## A measurement caught, not published

The harness token capture recorded 2,731,602 tokens for this 3-bug sprint - the whole
session's transcript, because it is the second sprint closed in one session, so it re-counts
RETRO-0061 and the incident recovery. That is ~13x the measured rate. It was **blanked from the
VELOCITY row as not-attributable** rather than published, and filed as **BG0236** (the
token-axis twin of BG0218): the capture must record a baseline at plan time and report a delta,
not an absolute.

## Next steps

- **CR0380** - re-verify an already-Done story's verifiers (BG0231's trigger half); the cheap
  static-resolution shape is likely, gated against adding test-execution cost.
- **BG0236** (High) - session-baseline the token capture so a second sprint in one session does
  not double-count.
- **RFC0048 option B** still the standing speed lever (test_gate.py is 56s of the suite), with
  D6's per-commit budget to be set against the improved baseline.
- Standing: **RFC0046** needs D1 closed or an override; **CR0319** is the release cut. Release
  freeze holds.

## Lessons this run paid for

L-0163 to L-0165 (RETRO-0062): a characterisation test still needs mutation to earn its keep (a
test that passes on first write because the code was already right may only decorate it); a
point-in-time acceptance criterion is manual by nature - an executable check re-asserting a
snapshot state un-Dones the story on unrelated drift; vacuity is not gated on exit 0, since a
runner that ran nothing proves nothing whatever its exit code.
