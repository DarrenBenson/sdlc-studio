# Reviews - LATEST (anchor)

> Derived from the sprint-close review of **RUN-01KXZ7YA** (a request closes itself when its
> children are all resolved, 2026-07-20, RETRO-0057). Supersedes the RETRO-0056 picture.

## Where the pipeline is (2026-07-20)

**RUN-01KXZ7YA is built, verified and reviewed**: 3/3 units, 8 points, closing review
**APPROVED at round 2** (one REJECT, one repair round, plus one MINOR fixed without a further
round). Goal judged **achieved**.

EP0087 delivers CR0364. US0269-US0271 carry the operator's reviewer-of-record sign-off.

**EP0085 (CR0358, 17 pts, US0261-US0265) is refined and next**, by operator decision. Its five
stories are skeletons - 8 `{{placeholder}}` blocks each - and the 17 points size the diff, not the
grooming, which sits on top and is unestimated.

## What shipped

- **US0269** - `reconcile detect` reports the new `request-derivable` drift kind, asking
  `transition._request_terminal_gate` rather than deciding for itself whether the children are
  resolved. The gate IS the predicate, so detector and gate cannot drift apart.
- **US0270** - `reconcile apply` derives the terminal through `transition`, so the index row, the
  parent cascade and the telemetry event all happen exactly as a hand transition would.
- **US0271** - the derivation refuses what G2 refuses: no childless request, no unresolved child,
  and a no-op where the two-backlog workflow is unenforced.

**G2 was a gate with no counterpart.** `transition` refused a premature request close but nothing
ever performed the closure once it was earned, so an enforcing project accumulated delivered
requests still reading as open work. Applied here: **35 requests derived Complete**, discovery
backlog **63 to 30**. Suite **3,267 skill + 243 tools green**, drift 1 (RFC0046, correctly blocked).

### A correction to the record

The commit message of `6a3138f` says of the 35 derived requests: *"Every one had already been
delivered."* **That claim is wider than its evidence.** The G2 gate inspects a request's CHILDREN,
never the request's own acceptance criteria - so `apply` closed 12 requests carrying residual ACs
of their own, and two of those (CR0302, CR0340) hold live defects. All twelve are recorded with
file:line evidence in **CR0365**; none is lost. The accurate statement is that every one had its
children delivered, which is what the derivation checks and all it can attest to.

## The CODE leg - two rounds

| Round | Findings | Outcome |
| --- | --- | --- |
| 1 | 4 MAJOR | REJECT |
| 2 | 1 MINOR (fixed, no further round) | APPROVE |

**Three of round 1's four MAJORs were honesty defects in a mechanism whose entire purpose is
reporting what it closed.** `--dry-run` consulted only the G2 gate and short-circuited past
`transition`, promising 36 derivations where the real sweep delivered 35. A refused derivation
printed to stderr, never counted as unapplied, so `apply` exited **0** on a blocked run and was
absent from the JSON payload entirely - a programmatic caller read it as clean. The drift hint sent
the operator to `reconcile apply` for RFC0046, a command that can never clear it.

**The fourth MAJOR is the author's known class recurring inside the commit written to fix it.**
`ac95397` fixed "tested the detector, claimed the apply path"; round 1 then found the apply-side
`two_backlog` guard had no test at all - mutating BOTH guards left the class green.

Round 2's single finding was a **comment**: the justification for the gate not blocking said *"no
commit can clear it"*, which is false for the case it cites - closing RFC0046's D1 is a commit, and
the refusal message names both remedies. Behaviour right, stated reason wrong. This is the third
consecutive run whose surviving defect was in prose written to justify code.

The reviewer re-derived the mutation table independently rather than trusting the author's, and
established that the `_story` fixture change was **load-bearing, not cosmetic**: with the old
placeholder status every `apply` in the class emitted a spurious unapplied row, so the exit-code
test would have passed vacuously on fixture noise rather than on the refusal it names.

**Two author verification steps were themselves broken** and are recorded because they could have
hidden a defect: a mutation check ran a non-existent test class, so the loader error read as a
kill; and a mutation run timed out mid-flight, left the mutant on disk, and the `cp` restore then
captured it - making the next baseline failure look like a code regression. Filed as **BG0215**.

## Next steps

- **EP0085 / CR0358** (High) - bound the review loop. Operator-selected as next, and now on **five**
  consecutive runs of evidence: review, not construction, is the cost centre. Groom US0261-US0265
  before building; the grooming is not in the 17 points.
- **RFC0048** - make the test suite cost-effective without lowering the floor. **D3** (a changed
  test must fail against a mutant of the code it pins, blocking) and **D6** (~60s per-commit budget,
  a ratchet that may be lowered but never raised) are SETTLED by the operator. D1, D2, D4, D5 open.
- **CR0365** (High) - the 12 residual-AC requests, including two live defects: CR0302's freshness
  guard is anchored to the stale number it exists to catch, and CR0340's `test_relevant` omits
  `help/` and `SKILL.md` though three tests read them.
- **CR0363** (High) - a mutation run scoped below its target's coverage over-reports absence. A hard
  prerequisite for RFC0048's D2 and for D3 at scale.
- **CR0366** (new) - `sprint plan` cannot see work already built and committed. EP0087 was fully
  delivered with its stories at Draft and no run open, so the planner forecast 675k tokens for a
  batch roughly 40 per cent done.
- **BG0215** (new) - a timed-out mutation harness leaves the mutant on disk and the restore
  captures it.
- **BG0216** (new) - a lesson gist containing bold markup makes the blocking `lessons-summary`
  gate lane unsatisfiable: the generator and the digest parser disagree on where the emphasis
  ends, so the same lesson reports as both added and removed and regenerating changes nothing.
  Hit during this close and worked around by rewording the lesson, which is not a fix.
- **CR0351** (M) - prose reaching a script through a shell argument lets a backtick silently empty
  the field it documents. Confirmed in the field by a second agent. **Still unbuilt** - artefacts
  filed this run deliberately avoided backticks in `--summary` arguments to work around it.
- **RFC0046** - reports `request-derivable` drift indefinitely until D1 is closed or a
  `Decision-Override` is recorded. That is the detector working, not noise.
- Standing: **CR0278** (interactive token capture), **CR0355** HELD until v5 (D0046). Residual audit
  CRs (CR0280-CR0306) remain unrefined. Release freeze held.

## Lessons this run paid for

L-0144 to L-0148. **Establish the baseline before the mutant, and restore from a source the mutant
cannot have touched** - a timed-out harness leaves the mutant on disk and a `cp` restore captures
it, after which every run measures the mutant while reporting on the code. **A test-runner error is
not a test failure** - any mutation result that does not name the specific test it killed is
unverified. **Prose written to justify code is code that has not been reviewed.** **Fixture noise
hides vacuous assertions.** **A drift kind whose advertised remedy cannot clear it is worse than no
hint** - where a later gate refuses, name that gate.
