# RETRO-0083: RUN-01KYNKDP: the ceremony gets cheaper, and the bug backlog goes to two

> **Date:** 2026-07-29
> **Batch:** BG0307, BG0308, BG0309, BG0310, BG0311, BG0320, BG0332, BG0333, BG0347, BG0354, BG0357, BG0359, BG0363, BG0364, BG0367, BG0368, BG0369, BG0371, BG0372, BG0373, BG0374, BG0385, BG0386, BG0387, BG0388, BG0389, BG0390, BG0391, BG0392, BG0393, BG0394, BG0395, BG0396, BG0397, BG0398, BG0399, US0479, US0531, US0532, US0533, US0553, US0554, US0555, US0556, US0557, US0558, US0559
> **Goal:** The ceremony costs less than the work it certifies and the open bug backlog reaches zero, so the discipline is cheap enough to keep running and nothing known-broken is carried into the next run
> **Delivered:** 47 / 48   **Blocked:** 1

## Delivered

- **EP0189 (US0553-US0559, 32pts)** - the close ceremony. `close --dry-run` reports every
  refusal of all seven steps in one read-only pass against a scratch copy; `critic` records a
  whole batch per verb; a missing argument is refused once before any write; the retro scaffold
  passes its own validator; the close records the gate verdict it earned and reports its own
  cost.
- **EP0181 (US0531-US0533, 11pts)** - `reconcile detect` reads the artefact corpus once per
  sweep instead of once per lookup, and the gate prints each lane's own seconds.
- **US0479 (2pts)** - a gate flag that was parsed and read by nothing, with the documentation
  that promised it.
- **36 bugs (98pts)** - all fifteen of RV0024's review residue, plus the older backlog: the
  measurement defects, the corpus-truth defects, and four specs describing a product other
  than this one.

## Blocked / deferred

- **BG0350 - dropped from the batch, deliberately.** Its Proposed Fix is to run a real
  adversarial pass over 25 already-Done stories and then remove the D0074 waiver. Recording
  verdicts for a review that did not happen would manufacture the evidence the gate exists to
  demand, and the pass itself is work this session cannot make independent of the run consuming
  its result. The reason is on the run record, not absorbed.

## What went well

- **The instruments this sprint built caught this sprint.** `close --dry-run` named all 15
  close refusals in one 2-minute pass; the previous run took three serial attempts of about
  400 seconds each to find the same class. `caller-check` over the batch is now a close step
  rather than a question an operator has to think of asking.
- **Every efficiency claim is a measurement, not an impression.** Gate 427s to 319s. Reconcile
  22.3s to 1.3s, with 777,732 file opens removed. 57 critic spawns to 3.
- **Three findings did not reproduce and were recorded as not reproducing** (BG0368, BG0373,
  and half of BG0371). In each case the finding's own Proposed Fix named something that WAS
  missing - always an assertion - and that is what shipped.

## What was hard / what stalled

- **A repair reached back into this sprint's own work.** BG0398 is correct, and applying it
  suspends the saving US0554 delivered two commits earlier: this repo has two readers of the
  `sdlc-studio` entry and one declarer, so unanimity correctly withholds the narrowing. Stated
  in the changelog and filed as BG0400 rather than papered over with a declaration that would
  not be true.
- **Binding `close-owed` to `--release` broke 26 existing tests**, which is how the real scope
  of that change made itself visible. The lane moved to the tag instead: `--release` is a
  contract consuming projects depend on.
- **Authoring criteria for the older bugs was unpriced work.** Eleven of them were filed with
  "no acceptance criterion could be derived", so the contract had to be written before the fix
  could be verified - a grooming cost carried by the delivery estimate.

## Lessons

- **A guard that answers a narrower question than it claims reports the narrow answer as the
  broad one.** Eight of RV0024's residue bugs were one shape: `caller-check --unit` kept the
  last value, `index_derived_issues` read four of five keys, the seam owner matched by
  substring, the waiver report was built from stories only. Each returned a clean verdict over
  something it had not looked at.
- **Verify the premise before repairing it, and record it when it does not hold.** Three
  findings this sprint did not reproduce. Checking cost minutes; the repairs they implied would
  have been changes to correct code, and the assertion each was actually missing is what
  shipped instead.
- **A speed-up test measures the wrong memo unless each is isolated.** Four mutants survived
  the corpus-cache work because the read-count test credited the by-id index for work the file
  memo underneath it was doing. Only per-memo tests could tell them apart.

## Carried lessons

- A guard that answers a narrower question than it claims reports the narrow answer as the broad one.
- Verify the premise before repairing it, and record it when it does not hold.
- A mechanism that reaches no caller is inert, however well it is tested.
- A test written by the author of a fix asserts the shape of the fix; mutation is how you find out.
- An enumerated list silently exempts what it forgot.

## Estimate vs actual

**Were the estimates any good?** The plan forecast a token cost per unit; telemetry recorded
what each one actually cost. This section holds the comparison, so the question is asked every
sprint instead of only when someone remembers to ask it.

The forecast is a hypothesis, not a settled calibration. Read the ratio, write down what it
implies, and change the constants only on evidence a human has looked at - a fit to a couple of
sprints fits noise.

<!-- accuracy:begin (generated by retro.py accuracy --write) -->
<!-- accuracy:end -->

- 143 of 148 planned points delivered across 47 of 48 units. The single miss is a deliberate
  drop, not an overrun, so the estimate held: the batch was sized correctly and the one unit
  that did not ship was refused on evidence grounds rather than on capacity.

## Actions raised

**Are there any CRs or Bugs you want to raise in this project to address any of the
issues found?**

This is the question that turns a retro into work. Every finding gets a disposition:
**file it** (a BG/CR id), **record it fixed in-sprint** (`fixed-in: <sha or unit>`), or
**decline it with a reason**. All three are green. What does not pass is silence - a
finding written down and left to rot. The three are counted separately at close: a sprint
that repaired eleven findings reads as eleven fixed, not eleven declined.

| Finding | Disposition |
| --- | --- |
| The read-map scanner attributes a fixture path to the real tree, suspending US0554's saving | BG0400 |
| 25 Done stories carry no independent critic verdict, waived under D0074 | BG0350 |
| RV0024's fifteen review-residue bugs | fixed-in: US0553-US0559 and the four bug commits of this run |
| The older measurement, corpus-truth and spec-drift backlog | fixed-in: RUN-01KYNKDP |
| Renaming the RFC index's `Spawned CRs` header to match its epic-holding cells | declined: a cross-file change touching the shipped template and three test files, for no behavioural gain - the detector reads a set of accepted spellings instead |
| Filling the 31 unfilled scaffolds with reconstructed content | declined: inventing what an author would have said is the false-evidence class this project files bugs about; each blank now states the absence |

<!-- file one with: scripts/file_finding.py · check with: scripts/retro.py dispose --id RETROxxxx -->

## Close loop (gated)

`gate --require-retro RETRO0083` (this retro's id, file form) fails until all four are true:

- [x] this retro exists AND passes its content check
- [x] its lessons are in the project store, not just in this file
- [x] open lessons re-validated: each is closed, extended, or within its horizon
- [x] `retros/LESSONS-SUMMARY.md` regenerated from the still-valid lessons

The next sprint reads them automatically: `sprint plan` prints the digest in the plan.

## Metrics

- Gate: 427s at the previous close to 319s here · Reconcile detect: 22.3s to 1.3s · Close
  refusal discovery: three serial ~400s attempts to one 2m read-only pass · Critic spawns per
  close: 57 to 3 · Open bugs: 37 to 2 · Mutants applied and killed: 41

## Handoff

- [HO-0037](../handoffs/HO0037-the-ceremony-costs-less-than-the-work-it.md) - 11 remaining item(s): 0 copilot-tail, 11 judgement. Pick up with `sprint plan --worklist sdlc-studio/.local/handoff-worklist.txt`.
