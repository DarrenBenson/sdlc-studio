# RETRO-0054: A small request decomposes into a shared batch epic: multi-parent links resolve, every refined story names the request it delivers, and the point total rolls in place

> **Date:** 2026-07-19
> **Batch:** EP0083, US0257
> **Goal:** A small request decomposes into a shared batch epic: multi-parent links resolve, every refined story names the request it delivers, and the point total rolls in place.
> **Delivered:** 2 / 2   **Blocked:** 0
>
> **RECONSTRUCTED.** This sprint shipped on 2026-07-17 across four commits and was closed with a
> full two-role review and operator sign-off - but no retro artefact was ever written. This retro
> was written on 2026-07-19 from the commit bodies, the artefacts and the close commit. Unlike
> RETRO-0053, the close record here is rich: the review, its finding, the repair and the sign-off
> are all recorded, so the reflective sections rest on real evidence rather than inference.

## Delivered

Delivered as CR0322 (RFC0045 D1), shipped across `a602caf`, `4807307`, `10a2435` and closed by
`5b10677` on 2026-07-17.

- **US0257 / EP0083** (5 pts) - `refine apply --into EPxxxx` lets a small request decompose its
  stories into an existing open epic instead of minting a singleton container. It points the
  request's `Decomposed-into` at that epic, adds one `Parent:` line per delivering request, and rolls
  the Derived Point Total. A terminal, non-epic or unknown target is refused with nothing minted;
  `--epic-title` and `--into` are mutually exclusive.
- The link core gained real multi-parent resolution: `sdlc_md.parent_refs` (plural), `children_of`
  membership, and a link-asymmetry gate that checks every `Parent` line - so a batch epic delivering
  several requests satisfies the two-backlog symmetry and derivation gates unchanged.
- **`Delivers:`** - added on operator design feedback mid-sprint. In a shared batch epic the
  request-to-story mapping has to be machine-resolvable, not merely implied by the story title. Every
  refined story now carries `> **Delivers:** <request>`; its Parent stays the epic, so derivation and
  the link gates were untouched. US0257 gained AC3 for it.

TDD throughout: 5 new `--into` tests at the first commit, 271 tests green across the ripple surface
(two_backlogs, reconcile, triage, amigo, migrate).

## Blocked / deferred

- None. US0257 Done, EP0083 Done, CR0322 Complete, RFC0045 Accepted by derivation, drift 0.

## What went well

- **The two-role close ran properly and caught a real defect.** An independent worktree critic,
  refute-framed with a reproduction required per claim, returned APPROVE after one repair round.
  Finding 1 was fixed test-first and then RE-VERIFIED by the same critic re-running its own repros -
  not by the author asserting the fix worked.
- **The finding was a genuine asymmetry, not a style note.** `_roll_point_total`'s increment regex
  was stricter than the `extract_field` presence check, so a non-bare Derived Point Total - an
  annotated `2 (derived)`, or a non-blockquote line - was either duplicated or silently left stale,
  and reconcile's mirror regex could not repair a wrong blockquote total. Two checks answering the
  same question with different strictness is the shape L-0128 later named.
- **The second finding was correctly filed rather than fixed.** The `parent_ref` / `parent_refs`
  divergence on a malformed record was inert, so it became BG0186 instead of scope creep in a
  closing review.
- **Operator design feedback landed mid-sprint without breaking the gates.** `Delivers:` was added,
  AC3 appended to the story, and the parent relationship deliberately left alone so derivation and
  link symmetry did not have to be re-argued.

## What was hard / what stalled

- **The close did everything except write the retro.** Review, verdict, evidence, sign-off,
  transitions and drift check all happened and are all recorded in `5b10677`. The one missing step
  was the artefact that feeds the next sprint's lessons. The ceremony was followed as a sequence of
  correct actions and still failed its purpose, which is a harder failure to notice than skipping it
  outright - the close commit reads as complete.
- **Existing shared-epic stories kept only title traceability.** The `Delivers:` field applies going
  forward and at grooming; stories refined before it existed were left Draft with the mapping implied
  by their titles. A known, accepted gap rather than a migration.

## Lessons

- **A close that performs every step except the record still leaves no record.** CR0322's close ran
  a two-role review, a repair round, a re-verification and an operator sign-off, and produced no
  retro - so none of that reached the lessons digest, and `close_owed` counted the units as
  unclosed for two days. Completeness of ceremony is not the same as the output the ceremony exists
  to produce.
- **When two checks answer the same question, the stricter one silently wins.** A presence check
  looser than the mutation regex meant a field could be seen but not updated. Extract one authority
  rather than keeping two that agree today.

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

- **Not recoverable, and not counted.** 5 points delivered over four commits. No plan-time forecast
  was recorded and the harness token total is not retrievable two days on, so this sprint contributes
  nothing to the estimator either way. Excluded rather than estimated, for the same reason as
  RETRO-0053: a reconstructed number would corrupt the rate rather than improve it.

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
| A close ran every step - review, repair, re-verification, sign-off, transitions, drift check - and still produced no retro, so nothing reached the lessons digest | CR0359 already open (sprint close discovers its blockers one at a time) covers the close chain's sequencing; this specific gap - a close that completes without its own output artefact - is the sharper case and is recorded here against it |
| `_roll_point_total`'s increment regex was stricter than the presence check that guarded it | declined: fixed in-run at `10a2435`, test-first, and re-verified by the reviewer that found it |
| `parent_ref` / `parent_refs` divergence on a malformed record | BG0186 - filed in-run, correctly triaged as inert rather than fixed inside a closing review |
| Stories refined before `Delivers:` existed keep only title traceability | declined: accepted at the time as a going-forward field applied at grooming, not a migration. Still true and still acceptable |

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

- Tokens: not-yet-captured (reconstructed; see Estimate vs actual) · Duration: not recoverable · Critic rejects: 1 (REJECT then APPROVE after one repair round)
