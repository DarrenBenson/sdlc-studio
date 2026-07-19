# RETRO-0052: The review loop is bounded and the close tells the truth about what it did: refine distributes criteria to the story that owns them, a goal-reached run does not read as stopped, and close-owed can reach zero

> **Date:** 2026-07-19
> **Batch:** BG0204, BG0205, BG0208, BG0210
> **Goal:** The review loop is bounded and the close tells the truth about what it did: refine distributes criteria to the story that owns them, a goal-reached run does not read as stopped, and close-owed can reach zero.
> **Delivered:** 4 / 4   **Blocked:** 0

## Delivered

- BG0205 (3 pts) - `refine` no longer seeds one story with its siblings' acceptance criteria. A
  multi-story breakdown seeds none and carries the request's criteria to the epic; a single-story
  breakdown is unchanged, because that story is the request. The batch's unblocker: refining any CR
  before this landed would have manufactured the grooming debt the batch exists to remove.
- BG0204 (1 pt) - a generated H1 has ONE definition, `sdlc_md.heading_title`. The MD026 trailing-stop
  defect had already been fixed twice in two generators, each fixing its own copy. Dogfooded at this
  very close: RETRO-0052's own H1 is derived from a Sprint Goal ending in a full stop and carries none.
- BG0208 (2 pts) - a close that completes with an `achieved` verdict records `goal-reached`. The real
  cause was not that the success path forgot: `_close_handoff` derives the outcome correctly but
  short-circuits when a handoff already exists, and that skip covered the outcome as well as the artefact.
- BG0210 (3 pts) - close-owed can reach zero. A derived epic inherits its children's coverage, so a
  clean close no longer manufactures unclearable debt for the epics it just derived. 35 epics forgiven,
  count 48 to 13 on one tree, every survivor genuinely uncovered.

## Blocked / deferred

- None. All four units reached Fixed, and the goal was reachable because the batch was bugs rather
  than stories - no two-role sign-off gate stands between a bug and terminal.

## What went well

- **Bounding the batch worked.** 4 units and 9 points against the previous run's 32 and 89. One
  review round found real defects, one repair round cleared them, and the second round APPROVEd -
  against five rejections last time. The change that mattered was scope, not effort.
- **Verifying the fix rather than the diff caught three separate things**: BG0205 reproduced in a
  clean workspace outside this repo; BG0210's real-repo count checked survivor by survivor; and the
  installed copy's suite run that surfaced BG0209 in the first place.
- **Neutral review briefs.** The earlier rounds were briefed with "this has rejected N times, assume
  the pattern continues", which primes for REJECT. Both rounds here were briefed with the diff and
  the risk surface only. One rejected, one approved, and both read as judgements rather than as
  confirmations of a supplied conclusion.
- **The gates earned their keep on the author.** The grooming gate refused a CR sized in story points
  instead of a T-shirt; the style guard caught internal provenance tags in a consuming-facing file;
  the close refused a stale review anchor, then an uncommitted one, then a missing critic verdict.
  Every refusal was correct.

## What was hard / what stalled

- **The obvious fix for BG0210 was wrong, and only checking stopped it shipping.** Appending derived
  epics to the retro's `Batch` is the natural move; `retro accuracy` sums points across the batch and
  an epic's Derived Point Total is the sum of its stories, so it would have double-counted every
  sprint's velocity from then on.
- **Two vacuous tests, both mine, both caught by mutation rather than by reading.** The BG0208
  fixture omitted a story index, so the tail returned early on drift and never reached the code under
  test. The first BG0210 type-guard test used bugs with no children, so the childless branch caught
  them and the test passed with the guard deleted.
- **Serial refusals cost real time.** Delivering one 3-point bug hit five anticipatable refusals,
  each behind a full gate run; the style one burned about 130 seconds of unit suite before reporting.

## Lessons

- **A test that passes for an incidental reason is not coverage.** Twice this sprint a guard looked
  covered because the path around it happened to be green: `_ac_heading`'s strip (every test used a
  long criterion, where truncation removes the punctuation anyway) and `close_owed`'s type guard
  (every test used childless non-epics). Mutating the guard is the only way to find this; reading the
  test cannot.
- **When two code paths answer the same question, extract before the second answer drifts.** The
  H1-strip rule had three private copies and the child-resolution rule had two. Both drifted, and
  both were found by someone else asking whether the "one definition" claim was true.
- **A fix's own argument constrains its implementation.** BG0208's case is that the archive is the
  permanent record - so re-stamping `ended_at` while correcting `outcome` corrupted the thing the fix
  existed to protect. Read the justification back against the diff.

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

- Forecast at plan time: 4 units, 9 points, ~225,000 tokens at the seeded 25,000/point rate. The
  build itself tracked close to it; the cost the forecast does not model is the CLOSE - two review
  rounds at roughly 115,000 subagent tokens each, plus the repair round between them. That is a
  structural gap, not a bad estimate: the model prices the delivery units and says nothing about the
  ceremony, and on a 9-point batch the ceremony is the larger half. Recorded rather than corrected -
  one sprint is not evidence for re-fitting a constant.

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
| Round-1 MAJOR: the `type_ != \"epic\"` guard was unpinned by the whole suite while the commit claimed every branch was mutation-killed | declined: no ticket needed - repaired in d9bf1d0, pinned by a test proven to fail when the guard is removed (CR0362: the vocabulary has no `fixed` state) |
| Round-1: coverage and derivation disagreed about what a child is | declined: no ticket needed - repaired in d9bf1d0, parser rehomed to `reconcile.declared_breakdown_ids` |
| Round-1: `heading_title` claimed to be the one definition while `_ac_heading` kept a private copy | declined: no ticket needed - repaired in d9bf1d0, `_ac_heading` routes through it so the claim is true rather than reworded |
| Round-1: the epic-criteria fallback emitted MD012-failing markdown | declined: no ticket needed - repaired in d9bf1d0 with a test on the fallback branch |
| Round-1: promoting the outcome moved `ended_at`, stretching the archived elapsed span | declined: no ticket needed - repaired in d9bf1d0, original end time restored and re-archived |
| Round-1: the promotion was reachable only from `--apply-signoff`, and the stated cause was wrong | declined: no ticket needed - repaired in d9bf1d0; the stated cause was wrong and is corrected in the record |
| Round-1: \"44 to 12\" compared two trees; \"about 38 epics\" was 35 | declined: no ticket needed - corrected in d9bf1d0 with the error named rather than quietly replaced |
| Round-2: `_ac_heading`'s strip unpinned by the entire suite | declined: no ticket needed - repaired in 3665f2c, short-criterion test across seven punctuation marks |
| Round-2: two full-tree `find_by_id` scans per epic | declined: no ticket needed - repaired in 3665f2c, one scan instead of two |
| Round-2: a failure restoring `ended_at` claimed the outcome was not stamped when it was | declined: no ticket needed - repaired in 3665f2c, the two steps report separately |
| Round-2: `_ac_heading` is a behaviour change presented as a refactor | declined: no ticket needed - documented at the call site in 3665f2c; the change is strictly better output |
| Round-2: an epic whose breakdown declares a dead id is owed a close no close can give | BG0211 - latent (zero such epics here), over-reporting direction |
| An agent meets the gates as refusals rather than as a briefing | CR0361 |
| A finding fixed during the sprint has no honest disposition - it is neither filed nor declined | CR0362 |
| Seven shipped tests read this repo's own story files, so the payload fails its own suite when installed | BG0209 |
| The close review is an unbounded repair loop with no convergence check or cost ceiling | CR0358 - the highest-value item this run produced, and NOT yet built |

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

- Tokens: not-yet-captured for the interactive build; the two review rounds cost ~115,000 and
  ~117,000 subagent tokens. Supply the harness total with `retro.py accuracy --tokens N`.
- Duration: one session. Critic rejects: 1 (round 1 REJECT on one MAJOR, round 2 APPROVE).

## Handoff

- [HO-0010](../handoffs/HO0010-the-review-loop-is-bounded-and-the-close.md) - 0 remaining item(s): 0 copilot-tail, 0 judgement. Pick up with `sprint plan --worklist sdlc-studio/.local/handoff-worklist.txt`.
