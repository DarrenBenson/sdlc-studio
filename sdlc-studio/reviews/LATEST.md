# Reviews - LATEST (anchor)

> Derived from the sprint-close review of **RUN-01KXVYGR** (the empty-the-backlog sprint,
> 2026-07-19, RETRO-0051). Supersedes the RETRO0050 picture.

## Where the pipeline is (2026-07-19)

The **empty-the-backlog sprint** (RUN-01KXVYGR) is **built, verified and reviewed**: 32/32 units
carry green acceptance criteria, 4 are terminal, **28 sit at Review awaiting the reviewer-of-record
sign-off**. The independent adversarial review **APPROVED at round 5**.

Sprint Goal verdict: **achieved**. The goal was phrased "the backlog is empty", which an autonomous
run can never reach - `two_role_after: 192` needs a sign-off past US0192, and
`critic.record_signoff` refuses a principal equal to the author or any reviewer already recorded,
including this session's own subagents. The reachable end state is "built, verified, reviewed, at
Review"; that should have been said at plan time (L-0112).

**To finish:** `sprint close --retro RETRO0051 --apply-signoff --principal "<you>"`. AC-verify
gated, so it refuses any unit whose criteria do not pass.

## What shipped

- **BG0197-BG0200** - the previous close's follow-ups: a mutation gate reporting unrun mutants as
  survivors, a close skipping its velocity row silently, a handoff adopting another run's identity,
  two id readers disagreeing on width.
- **EP0079** - the RFC accept gate is mechanical; the finding filer derives its decision row.
- **EP0082** - scanners survive a corrupt artefact, `gate --release` binds `check_versions
  --strict`, the green-run noise gate runs, the CR-index Linked Epics column is censused.
- **EP0073/EP0074/EP0078** - the audit estimate learns from recorded actuals; `sprint report` is
  reachable by a route and drawn at the close; `review generate` folded into `audit --profile repo`.
- **EP0076** - a rolling policy regenerates the plan at each boundary, per-cycle run-state archival.
- **EP0081** - catalogue regrouped around the process spine, command-audit drift back to 0.

Suite **3,173 green**, tools **236 green**, drift 0, validate 0 errors, every commit gated.

## The CODE leg - five rounds

The adversarial full-diff review ran five times, rejecting four. Filed as **CR0358** (High).

| Round | Findings | Production files touched |
| --- | --- | --- |
| 1 | 2 MAJOR + 4 MINOR | `reconcile.py`, `run_state.py`, `transition.py` |
| 2 | 2 MAJOR + 3 MINOR | `run_state.py`, `transition.py` |
| 3 | 1 MAJOR + 2 MINOR | `run_state.py`, `transition.py` |
| 4 | 1 MAJOR + 1 MINOR | `transition.py` |
| 5 | APPROVE, 3 MINOR | `transition.py` |

**Round 1 earned its keep**: six false negatives, including `apply_linked_epics` destroying the
**Date** cell on every apply, and a noise gate whose baseline of 68 measured its own blind spot
(true count 233). **Rounds 2-4 were different in kind** - each MAJOR was created by the previous
round's repair, all three inside `_rfc_open_decisions` (one 40-line function), at roughly 80k
tokens per round with nothing noticing. The correct move after round 2 was to revert or rewrite
that function, not patch again. The recurring class across all five rounds was **prose asserting a
completeness the code did not have**. Full detail in RETRO0051.

## Next steps

- **The sign-off** is the blocking step. 28 units wait on it.
- **CR0358** (High) - the close review is an unbounded repair loop: no convergence check, no round
  ceiling, no cost surface, and the author writes the reviewer's prompt. Highest-value follow-up.
- **CR0351** (widened, M) - prose reaches 13 scripts through a shell argument, so a backtick
  silently empties the field it documents. File/stdin form is the fix; the detector catches 3 of 4
  real corruptions and is defence in depth only.
- Filed this run: **BG0201-BG0207**, **CR0346-CR0358**. Notable: **BG0202** (confinement sweep
  blind to `path.open(mode)`), **BG0203** (4 mutation survivors; 15 of 654 sampled, a floor not a
  count), **BG0207** (the RFC gate can report one open decision when two are), **CR0356**
  (`reconcile` has no title-drift kind, so a retitled artefact drifts silently).
- **CR0355** is **HELD until v5 launch** (D0046) - the Claude for Open Source acknowledgement; the
  logo needs prior written permission and must never delay the release.
- **D0043** records two ACs resting on inference (US0232 AC2, US0234 AC1); **D0042** the five
  help-only command dispositions. **13 duplicated Verify selectors** remain workspace-wide.
- Standing: **CR0278** - this run's tokens are **not-yet-captured**; supply with `retro.py accuracy
  --tokens N`. Residual audit CRs (CR0280-CR0306) remain unrefined. Release freeze held.

## Lessons this run paid for

L-0104 to L-0126. Most transferable: **story points size the diff, not the discovery**; **the
author cannot close the loop**; and **a fail-closed fallback is not the main path with one rule
removed** (L-0126) - decide what the safe answer IS, and give a guard shadowed by a safety net a
test whose correct answer is PASS, the one answer the net cannot produce.
