# Reviews - LATEST (anchor)

> Derived from the sprint-close review of **RUN-01KXVYGR** (the empty-the-backlog sprint,
> 2026-07-19, RETRO-0051). Supersedes the RETRO0050 picture.

## Where the pipeline is (2026-07-19)

The **empty-the-backlog sprint** (RUN-01KXVYGR) is **built, not closed**: 32/32 units carry green
acceptance criteria, 4 are terminal, and **28 sit at Review awaiting the reviewer-of-record
sign-off**. Sprint Goal verdict: **partial**, and the reason is structural rather than a shortfall
in the work - `two_role_after: 192` means every story past US0192 needs a sign-off, and
`critic.record_signoff` refuses a principal equal to the author or matching any reviewer already
recorded, explicitly including the authoring session's own subagents. A goal phrased as "the
backlog is empty" was never reachable by an autonomous run; the reachable end state is "built,
verified, at Review". That should have been said at plan time.

**To finish the run:** review the decision brief, then
`sprint close --retro RETRO-0051 --apply-signoff --principal "<you>"`. It is AC-verify gated, so it
refuses any unit whose criteria do not actually pass.

## What shipped

- **BG0197-BG0200** (Fixed) - the previous close's follow-ups: a mutation gate reporting unrun
  mutants as survivors, a close skipping its velocity row in silence, a handoff adopting another
  run's identity, two id readers disagreeing on width.
- **EP0079** - the RFC accept gate is mechanical (`transition` refuses, `validate` covers the files
  that predate it), the finding filer writes a decision row derived from the finding's own options,
  and the accepted tranche records what shipped.
- **EP0082** - scanners survive a corrupt artefact, `gate --release` binds `check_versions
  --strict`, the green-run noise gate actually runs, write-confinement covers a derived roster, and
  the CR-index Linked Epics column is censused.
- **EP0078** - `review generate` folded into `audit --profile repo`; one weakness-hunt, one name.
- **EP0073** - the audit estimate learns from recorded actuals; capped candidates carry over.
- **EP0074** - `sprint report` is reachable by a route and drawn at the close.
- **EP0076** - a rolling policy regenerates the plan at each boundary, with per-cycle run-state
  archival so a closed cycle stays auditable.
- **EP0081** - four help-only commands promoted, `upgrade` folded behind `migrate`, the catalogue
  regrouped around the process spine, command-audit drift back to 0.

Full suite 3,159 green, tools 233 green, drift 0, every commit gated.

## The CODE leg - and its gap

**No independent adversarial full-diff review has been run on this batch.** That is the one leg the
close is missing, and it is the substance of the sign-off ask rather than a formality: the previous
two sprints were each REJECTed twice by exactly that pass, both times for claiming completion on
incomplete evidence.

What stood in for it during the build was self-mutation, which caught more than a reading pass
would have:

- **Seven non-discriminating tests**, six written by this session. Every one was found by mutating,
  none by reading. Two survived their first mutation attempt because the *mutation* was inert - a
  failure mode of mutation testing itself, diagnosed rather than recorded as a false clean.
- **Three false-negative detectors**, the dominant defect shape in this codebase: a placeholder
  check matching one literal phrase (BG0201), a noise detector catching 0 of 68 real leaks
  (US0253), a confinement sweep blind to `path.open(mode)` (BG0202).
- **Four artefacts naming the wrong files** - US0240, US0246, US0252, and CR0295's tranche was
  three short. All found by measuring, never by reading.

## Next steps

- **The sign-off** is the blocking step. 28 units wait on it.
- Follow-ups filed this run: **BG0201** (Fixed - the tranche audit certified 28 unfilled templates
  as ready), **BG0202** (the confinement sweep cannot see `path.open(mode)`), **BG0203** (4
  mutation survivors in the new audit profile parser; the run sampled 15 of 654 enumerated
  mutants, so that is a floor on the gap), **BG0204** (retro scaffolding keeps the Sprint Goal's
  full stop in the H1 - BG0179's defect in a second generator).
- **Two ACs rest on inference beyond CR0320** (US0232 AC2, US0234 AC1), recorded as D0043 for the
  review to judge as inferences rather than find as surprises. **D0042** records the five
  help-only command dispositions and is reversible.
- **13 duplicated Verify selectors** remain workspace-wide, carried from the previous run.
- Standing: **CR0278** (interactive-sprint token capture) - this run's tokens are
  **not-yet-captured**; supply with `retro.py accuracy --tokens N`.
- Residual audit CRs (CR0280-CR0306) and the discovery backlog remain unrefined.
- Release freeze held; everything landed unreleased on `main`.

## Lessons this run paid for

L-0104 to L-0113. The two most transferable: **story points size the diff, not the discovery**
(every epic overran, never on typing - the overrun was always measurement contradicting a written
claim), and **the author cannot close the loop** (an autonomous run drives a batch to built and
verified; the terminal transition is deliberately out of its reach).
