# RETRO-0040: Backlog triage as a ceremony inside plan

> **Date:** 2026-07-16
> **Batch:** US0167, US0168, US0169, US0170, US0171 (EP0047, from RFC0037, absorbing CR0264)
> **Goal:** done
> **Delivered:** 5 / 5   **Blocked:** 0

## Delivered

- **US0167/US0168 (10pt) - the lens engine.** `backlog_triage.py` runs deterministic lenses over the
  non-terminal backlog: DUPLICATE/SUBSUMED (shared `Affects` + token-Jaccard wording), OVERSIZED
  (points > 8 blocks), STALE (old, undepended), ORPHANED-DEPENDENCY (a `Depends on:` that is terminal
  or absent). Each lens tested on a positive AND a negative.
- **US0169 (3pt) - filing-time detection (CR0264).** `file_finding` warns when a new finding overlaps
  an open artefact, candidate named, before the id is minted - never a refusal.
- **US0170 (5pt) - triage inside `plan`.** The judgement lenses surface in the plan the operator
  already reads (reporting-only); the mechanical oversized lens is the breakdown gate's to block.
- **US0171 (2pt) - status advisory.** A backlog-triage summary on `status`/`hint`.

## Blocked / deferred

- Nothing blocked. RFC0037 Accepted (children Done); it ABSORBED CR0264, now Superseded.

## What went well

- **One overlap primitive, three surfaces.** Filing-time detection, the plan pass, and the status
  advisory all read the same lens engine, so the cheap moment and the planning moment agree by
  construction rather than by two hand-kept copies.
- **The lenses are clean on the real backlog** (no false positives across 18 open artefacts), while
  every lens has a passing positive test - the negative-and-positive discipline caught two
  similarity-threshold bugs during the build.

## What was hard / what stalled

- **The independent review found a shared-library robustness bug, not just a local one - and my
  first fix landed one layer too high.** The filer's duplicate check could crash a filing when any
  sibling artefact was unreadable. I fixed `sdlc_md.iter_artifact_files` (it caught only `OSError`,
  so a non-UTF-8 file crashed every scanner) - correct, but INCOMPLETE: the re-review drove the
  end-to-end filer path and showed the crash had merely RELOCATED to `reconcile.file_census`, which
  does its own `read_text` and is on both the filer's post-write recompute and the `reconcile detect`
  drift gate - now crashing AFTER the artefact and its index row were written (a partial write, worse
  than before). The true fix was a shared `read_text_safe` helper routed through `file_census` and the
  ~12 other artefact-body reads in reconcile/close_owed, plus an END-TO-END test that drives
  `file_finding.file_finding()` with a bad sibling (the isolated helper test gave false confidence).
  Four more findings (orphaned-dep false positives on live non-triage-type deps; a future/prose date
  defeating staleness; no drop accounting; a pointed container escaping the oversized lens) all fixed
  with regression tests.
- **The author cannot record its own review.** The harness self-approval guard refused the primary
  agent recording the critic APPROVE verdicts, because the "independent" reviewer is a subagent the
  same agent spawns and prompts - mechanically self-review however adversarial the pass actually was.
  Surfaced to the operator, who is the real independent party. A correct guard: it is exactly the
  author!=reviewer principle this project enforces, applied to the agent itself.

## Lessons

- A crash inside a shared file-walk (`iter_artifact_files`) is not a local bug in the feature that
  tripped it - it is a latent fault in every consumer. When a review finds "feature X breaks on a bad
  file", check whether the shared enumerator, not X, is the thing that should tolerate it: fixing it
  once at the library hardens every scanner rather than patching one call site and leaving the rest
  exposed. A `read_text` in a shared walker must catch `UnicodeDecodeError` as well as `OSError`.
- But fixing ONE enumerator is not fixing the invariant: sibling code paths (`reconcile.file_census`
  and a dozen direct `read_text` calls) bypass the enumerator entirely, so the crash relocated past
  the write and left a partial write - strictly worse. A robustness invariant ("one bad file never
  crashes a scanner") must be verified END-TO-END on the real public entry point, not on the helper
  in isolation: a test that exercises only the guarded function passes while the unguarded sibling on
  the same call path still crashes. When you claim "every scanner is now safe", grep every `read_text`
  on that path and drive the invariant through the front door.
- A grandfather/coherence check that resolves ids against a PARTIAL set (only the triage-type,
  non-terminal backlog) will false-flag anything outside that set. An orphaned-dependency lens must
  resolve against ALL artefact types and distinguish terminal (resolved) from absent (mistyped), or
  it calls a live dependency broken and gives wrong advice. Resolve against the whole namespace, then
  classify.
- A "last-touched" date read as `max(every date in the file)` is defeated by any future or prose date
  (a deadline in the summary). Anchor a staleness date on the metadata fields and the revision-history
  region only, and clamp to today - a date in the future is not a date the artefact was touched.

## Estimate vs actual

The plan forecast ~500,000 tokens (20 points x the ~25,000 seed). Harness-tracked, so
**not-yet-captured** here rather than unmeasurable; supply it with
`retro.py accuracy --id RETRO0040 --tokens N --write` to record a real tokens-per-point over the 20
delivered points. Descriptive only, never a target (CR0273).

<!-- accuracy:begin (generated by retro.py accuracy --write) -->
<!-- accuracy:end -->

- Not-yet-captured, not unknowable.

## Actions raised

**Are there any CRs or Bugs you want to raise in this project to address any of the issues found?**

| Finding | Disposition |
| --- | --- |
| The filer (and every scanner) crashed on a non-UTF-8 artefact - `iter_artifact_files` caught only OSError (found in review) | declined: no ticket - fixed this sprint at the library (`except (OSError, UnicodeDecodeError)`) + regression test. |
| Orphaned-dep false-flagged live deps on non-triage-type artefacts; conflated terminal with absent (found in review) | declined: no ticket - fixed this sprint (resolve against all types; distinguish resolved from absent) + tests. |
| A future/prose date suppressed the stale lens; no drop accounting for unreadable files (found in review) | declined: no ticket - both fixed this sprint (anchor + clamp the date; a `skipped` count surfaced) + tests. |
| The 0.5 similarity threshold is brittle on very short titles/summaries | declined: reporting-only lens, the human confirms each candidate; acceptable and documented. |
| The author cannot independently record its own critic verdict (harness self-approval guard) | declined: no ticket this sprint - the operator signed off as reviewer of record and the verdicts were recorded on their say-so; the deeper question (adversarial reviewer vs reviewer-of-record as distinct roles) is being raised as its own RFC. |

<!-- file one with: scripts/file_finding.py -->

## Close loop (gated)

- [x] this retro exists AND passes its content check
- [x] its lessons are in the project store
- [x] open lessons re-validated
- [x] `retros/LESSONS-SUMMARY.md` regenerated

## Metrics

- Tokens: not-yet-captured (harness-tracked; supply with `accuracy --tokens N`) · Duration: one session · Critic rejects: 2 (Dani REQUEST-CHANGES twice - first a shared-library robustness MAJOR + 4 correctness MINOR/NIT; then the MAJOR's residual: the first fix landed one layer too high and the crash relocated past the write. Both fully fixed with end-to-end regression tests; the two-round review is the story of this sprint)
