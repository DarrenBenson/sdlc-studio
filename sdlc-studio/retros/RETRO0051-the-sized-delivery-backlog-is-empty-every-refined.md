# RETRO-0051: The sized delivery backlog is empty: every refined epic and every open bug ships, leaving only unrefined discovery options

> **Date:** 2026-07-19
> **Batch:** BG0199, BG0197, BG0200, US0224, US0225, US0231, US0235, US0240, US0241, US0242, US0243, US0246, US0251, US0252, US0222, US0223, US0229, US0230, US0233, US0234, US0239, US0244, US0245, US0249, US0253, US0254, US0256, BG0198, US0221, US0232, US0250, US0255
> **Goal:** The sized delivery backlog is empty: every refined epic and every open bug ships, leaving only unrefined discovery options.
> **Delivered:** 32 / 32 built (4 terminal, 28 at Review awaiting sign-off)   **Blocked:** 0

## Delivered

All 32 batch units are BUILT with their acceptance criteria green. Four are terminal; 28 sit at
Review because `two_role_after: 192` requires a reviewer-of-record sign-off, and
`critic.record_signoff` refuses a principal equal to the author or matching any reviewer already
recorded - which explicitly includes this session's own subagents. That is the gate working.

- **BG0197-BG0200** (Fixed) - the close-chain follow-ups from the previous run: a mutation gate
  that reported unrun mutants as survivors, a close that skipped its velocity row in silence, a
  handoff that adopted another run's identity, and two id readers disagreeing on width.
- **EP0079** (US0244-US0246) - the RFC accept gate is mechanical, the finding filer writes a
  decision row that says something, and the accepted tranche records what shipped.
- **EP0082** (US0252-US0256) - scanners survive a corrupt artefact, the release gate binds the
  strict version check, the noise gate actually runs, write-confinement covers a roster, and the
  Linked Epics column is censused.
- **EP0078** (US0239-US0243) - `review generate` folded into `audit --profile repo`; one
  weakness-hunt, one name, with the refute panel wired to every profile.
- **EP0073** (US0221, US0222) - the audit estimate learns from recorded actuals; capped-out
  candidates are carried over rather than lost.
- **EP0074** (US0223-US0225) - `sprint report` is reachable by a route and drawn at the close.
- **EP0076** (US0229-US0235) - a rolling policy regenerates the plan at each boundary, with
  per-cycle run-state archival so a closed cycle stays auditable.
- **EP0081** (US0249-US0251) - four help-only commands promoted, `upgrade` folded behind
  `migrate`, the catalogue regrouped around the process spine, drift back to 0.

Filed in-run and outside the batch: **BG0201** (Fixed) and **BG0202** (Open).

## Blocked / deferred

- Nothing blocked. The 28 units at Review are not blocked; they await the one step the authoring
  session is architecturally barred from taking.
- **BG0202** (filed, not fixed): the confinement roster sweep cannot see `path.open(mode)`, so a
  module whose only write takes that form slips the roster. Deliberately not absorbed - it is a
  defect in a guard this sprint shipped, and it deserves its own unit rather than a same-sprint
  patch by the author of the guard.
- **13 duplicated Verify selectors** remain across the workspace, carried forward from the
  previous run. Untouched here.

## What went well

- **The readiness gate was made honest before any work started.** The tranche audit reported
  32/32 ready over 28 stories that were pure unfilled template. Fixing that (BG0201) turned the
  batch from apparently-groomed into demonstrably-ungroomed, which is what made the rest real.
- **Every AC was proven red before implementation.** After grooming, a full-batch `verify_ac`
  sweep reported pass=0 fail=73. A green that has never been red is not evidence.
- **Cross-story auditing worked.** US0255's confinement suite caught an atomicity violation in
  US0256 within minutes of existing; US0221's implementation then caught a hole in US0255's own
  detector. Neither was reachable from its own story's ACs.
- **Delegated agents reported their own weak tests.** One flagged a test of its own that passed
  before the feature existed; another diagnosed a surviving mutant as a bad MUTATION rather than
  a bad test, preventing a false non-discriminating finding.
- **Refusals held.** An agent refused to stage a file to force a post-commit AC green, calling it
  manufacturing evidence. Another refused to delete a working command to satisfy an AC's wording.

## What was hard / what stalled

- **The specifications were wrong more often than the code.** Four artefacts named the wrong
  files (US0240, US0246, US0252, and CR0295's tranche was three short). Every one was found by
  measuring, never by reading.
- **Detectors that matched one form of a defect and were read as matching the defect.** Three
  separate instances: the placeholder check (one literal phrase), the noise detector (0 of 68
  real leaks), the confinement sweep (`open()` but not `path.open()`). This is the dominant
  defect shape in this codebase and it should be a standing review question.
- **Non-discriminating tests, seven of them**, six mine. Every one was caught by mutating, none
  by reading. Two survived their first mutation attempt because the MUTATION was inert.
- **Parallel work collided because I scoped by `Affects`.** US0252 and US0256 were recorded as
  colliding on `reconcile.py`; correcting one `Affects` dissolved the record while both still
  wrote the same test file. The collision analysis inherits the accuracy of data this very run
  proved unreliable.
- **A pre-existing markdownlint failure was invisible** until a change touched its file, because
  the gate lints only what changes.
- **The mutation gate refused, and it was right.** A red baseline blocked the close. The cause was
  a test I wrote this sprint for BG0197: it populated a `__pycache__` via a subprocess that
  inherited `PYTHONDONTWRITEBYTECODE=1` from the mutation harness - the env my own BG0197 fix
  sets - so its precondition silently vanished and it failed only when invoked through the gate.
  A fixture must establish its own preconditions, not borrow them from the parent process.
- **I hit a lesson this repo had already recorded** (L-0079, backticks in shell-quoted text are
  command substitutions) while writing a lesson about something else.

## Lessons

- **L-0104** A readiness gate that recognises one hardcoded placeholder recognises none.
- **L-0105** Suppressing a cache write does not stop a cache read.
- **L-0106** A same-length mutant is the mutation check's own blind spot.
- **L-0107** An AC that runs the repo's standing guards is green before the work starts.
- **L-0108** Build the gate first, then let it tell you the size of the backlog it guards.
- **L-0109** Delegating by `Affects` reproduces whatever is wrong with the `Affects`.
- **L-0110** A new writer must join the atomicity and confinement rosters, not just work.
- **L-0111** Story points size the diff, not the discovery.
- **L-0112** The author cannot close the loop: build-to-Done needs the reviewer of record.
- **L-0113** An AC asserting the committed state cannot be green in the working tree.

## Estimate vs actual

**Were the estimates any good?** The plan forecast a token cost per unit; telemetry recorded
what each one actually cost. This section holds the comparison, so the question is asked every
sprint instead of only when someone remembers to ask it.

Generate it: `scripts/retro.py accuracy --id RETROxxxx --write` - it fills the block below from
the batch's telemetry and appends this sprint's row to `retros/VELOCITY.md`.

A unit with no per-unit telemetry record has its PER-UNIT ratio reported as **UNMEASURED** and
excluded from that ratio - it is never counted as accurate. But the token count itself is NOT
unmeasurable: the harness tracks it deterministically. An INTERACTIVE sprint (no runner) records no
per-unit actual, so supply the harness-tracked sprint total with `accuracy --tokens N` to get a
real sprint tokens-per-point over the delivered points - report it as **not-yet-captured** until you
do, never as if the number were unknowable. That figure is DESCRIPTIVE, never a target (see CR0273).

The forecast is a hypothesis, not a settled calibration. Read the ratio, write down what it
implies, and change the constants only on evidence a human has looked at - a fit to a couple of
sprints fits noise.

<!-- accuracy:begin (generated by retro.py accuracy --write) -->
<!-- accuracy:end -->

- The 89-point forecast priced the EDIT and could not price the DISCOVERY. Every epic overran,
  and never on typing: US0256 (3pts) needed a detector, an applier, two CLI paths, a `refine`
  integration and three roster registrations; US0244 (3pts) found its own gate had a false
  negative on real data; US0253 (5pts) found the gate it was wiring had never run. Points derived
  from an unverified decomposition are a lower bound with wide error bars, and should be stated
  that way at plan time rather than defended at the close.

## Actions raised

**Are there any CRs or Bugs you want to raise in this project to address any of the
issues found?**

This is the question that turns a retro into work. Every finding gets a disposition:
**file it**, or **decline it with a reason**. Both are green. What does not pass is
silence - a finding written down and left to rot.

To say "nothing worth raising", say so in a row and give the reason. An empty table is
not an answer.

| Finding | Disposition |
| --- | --- |
| Tranche audit certified 28 unfilled templates as ready | BG0201 - filed and Fixed in-run |
| Confinement roster sweep cannot see `path.open(mode)` | BG0202 - filed, deliberately left Open |
| 4 mutation survivors in the new audit profile parser | BG0203 - filed; found by the close's mutation gate, not the epic's own tests |
| Retro H1 derived from the Sprint Goal keeps its full stop, blocking the close commit on MD026 | BG0204 - filed; the same defect a sibling generator was already fixed for |
| My BG0197 test was not hermetic: it failed under the very env its own fix sets | declined: fixed in-run, so there is nothing left to file - the fixture now forces bytecode on rather than inheriting the parent's setting |
| `command_audit.SPINE` maps `retro` to `utility`, arguably sprint-and-review | declined: re-curating a map other tooling reads is not a same-sprint change by the agent who noticed it - raise separately if the operator agrees |
| US0251 AC2 is a post-commit guard wearing a pre-commit criterion's clothes | declined: the AC is correct about the committed state, and D0044 records how it is verified - reword only if it recurs |
| 13 duplicated Verify selectors remain workspace-wide | declined: carried from the previous run and explicitly earmarked there as a batch of its own |
| US0232 AC2 and US0234 AC1 rest on inference beyond CR0320 | declined: not defects - recorded as D0043 and flagged for the closing review to judge as inferences |

<!-- file one with: scripts/file_finding.py · check with: scripts/retro.py dispose --id RETROxxxx -->

## Close loop (gated)

`gate --require-retro RETROxxxx` (this retro's id, file form) fails until all four are true:

- [ ] this retro exists AND passes its content check - required sections, at least one real
      lesson, and every finding dispositioned (`retro.py validate --id RETROxxxx`)
- [ ] its lessons are in the project store, not just in this file (`retro.py extract --id RETROxxxx`)
- [ ] open lessons re-validated: each is closed, extended, or within its horizon (`lessons revalidate`)
- [ ] `retros/LESSONS-SUMMARY.md` regenerated from the still-valid lessons (`lessons summary`)

The next sprint reads them automatically: `sprint plan` prints the digest in the plan.

## Metrics

- Tokens: not-yet-captured (interactive sprint; supply with `retro.py accuracy --tokens N`)
- Duration: one extended interactive session · Critic rejects: 0 formal rounds - no independent
  adversarial full-diff pass has been run on this batch yet, which is the gap the sign-off must
  close. Seven non-discriminating tests and three false-negative detectors were caught by
  self-mutation during the build, not by a review pass.
