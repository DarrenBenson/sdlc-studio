# Reviews - LATEST (anchor)

> Derived from the sprint-close review of **RUN-01KXXERR** (an agent is briefed by the gates
> before the work, 2026-07-19, RETRO-0056). Supersedes the RETRO-0055 picture.

## Where the pipeline is (2026-07-19)

**RUN-01KXXERR is built, verified and reviewed**: 5/5 units, 17 points, closing review
**APPROVED at round 3** (two REJECTs, two repair rounds). Goal judged **achieved**.

EP0086 delivers CR0361. BG0212 and BG0213 are Fixed and terminal; US0266-US0268 carry the
operator's reviewer-of-record sign-off.

**EP0085 (CR0358, 17 pts, US0261-US0265) is refined and next**, by operator decision. Its
stories are skeletons and need grooming before any code.

## What shipped

- **BG0213** - `transition --dry-run` gives the same answer as the real run. It skipped the
  bug-depth, depth-parity and AC-verify gates, so a bug with no `Verification depth` was reported
  as `would set ... Fixed` while the real run blocked it. Found while grooming US0267.
- **US0268** - the pre-commit gate runs cheapest-first AND short-circuits. Reordering alone saves
  nothing, because `run()` records a failure and returns 0; the expensive block needed its own
  guard. Measured: a markdown-only defect reports in 35s instead of ~132s.
- **US0267** - `transition requirements` asks what a close needs before the work, derived by
  running the real gates rather than restating them.
- **US0266** - `sprint plan` briefs the gates each unit will meet, generated from
  `gate.DEFAULT_CHECKS` and the transition gates, scoped to the batch.
- **BG0212** - `audit.py` mutation survivors 15 to 6, the six shown equivalent by construction.

Suite **3,243 green**, drift 0, noise baseline **233 to 134** by capturing leaks, not raising it.

## The CODE leg - three rounds

| Round | Findings | Outcome |
| --- | --- | --- |
| 1 | 1 MAJOR + 4 MINOR | REJECT |
| 2 | 1 MAJOR | REJECT |
| 3 | none outstanding | APPROVE |

**Every MAJOR in every round was about a TEST, not about shipped behaviour.** Round 1:
`requirements` rebuilt its list by splitting a sentence, and the pinning test passed because its
fixture happened to carry one suffixed block. Round 2: the replacement test was **tautological** -
it built the exception by hand, so the defective code never ran, and re-introducing the merge left
**326 tests green**. The code fixes held throughout; the evidence for them did not.

The reviewer recorded its own caveat: it authored the round-2 finding and verified its own fix, so
that chain is single-reviewer and covers technical verification, not role separation.

**COST, measured for the first time:** the three rounds cost ~181k + ~213k + ~220k subagent tokens,
over **600,000 against a 425,000-token forecast for the whole batch**. The review cost more than
the forecast for the work.

## Next steps

- **EP0085 / CR0358** (High) - bound the review loop. Operator-selected as next. Four consecutive
  runs of evidence and now a hard number. Groom US0261-US0265 before building.
- **RFC0048** (new) - make the test suite cost-effective without lowering the floor. Two decisions
  are SETTLED by the operator: **D3 - a changed test must fail against a mutant of the code it
  pins, as a BLOCKING gate**; **D6 - the per-commit gate budget is ~60s, enforced as a ratchet
  that may be lowered but never raised**. D1, D2, D4 and D5 remain open. Measured: three test
  files are 62 per cent of the suite runtime and 14 per cent of the tests, `test_gate.py` alone
  41 per cent.
- **CR0351** (M) - prose reaching a script through a shell argument lets a backtick silently empty
  the field it documents. **Now confirmed in the field**: another agent had a bug record corrupt
  itself on filing, with the partial failure reported as a cheerful success. Escalated.
- **CR0363** (High) - a mutation run scoped below its target's coverage over-reports absence. A
  hard prerequisite for RFC0048's D2, and for D3 at scale.
- Filed this run: **BG0214** (`artifact.py close --dry-run` still promises a close the real run
  refuses - pre-existing, and it means BG0213's framing was wider than its fix).
- Standing: **CR0278** (interactive token capture), **CR0355** HELD until v5 (D0046). Residual
  audit CRs (CR0280-CR0306) remain unrefined. Release freeze held.

## Lessons this run paid for

L-0140 to L-0143. **A test that cannot fail is worse than no test, because it reads as coverage** -
re-introduce the defect a new test claims to pin and watch it go red. **A fixture can satisfy an
assertion for a reason unrelated to the property under test** - choose the fixture that
discriminates, not the one to hand. **Rebuild structure from data, never from prose.** **The gate
cost is concentrated, not diffuse** - three files, not 3,243 tests.
