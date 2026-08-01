# RV0025: RUN-01KYY52D closing review - the review learned to discriminate, and then failed its own new rule

> **Date:** 2026-08-01
> **Run:** RUN-01KYY52D
> **Verdict:** APPROVE (every finding repaired in-batch and confirmed by a fresh independent pass)
> **Reviewers:** four independent contexts, none of which wrote the code
> **Author:** Claude Opus 5

## What was reviewed

Nine units, 36 points, across two epics, in four independent passes. Every pass took its
brief from `critic.py brief` rather than a hand-written prompt, and each was bounded to the
unit's declared `Affects` against the run's base ref.

| Pass | Scope | Base | Outcome |
| --- | --- | --- | --- |
| EP0195 boundary | US0583, US0584, US0585, US0597 | `3c195846` | APPROVE US0584; REJECT three |
| EP0194 boundary | US0577-US0580, US0582 | `3570c94a` | APPROVE US0579, US0582; REJECT three |
| BG0484 confirmation | the EP0194 repair diff | `a0e72a62~1` | APPROVE, all five findings CLOSED |
| BG0479-82 confirmation | the EP0195 repair diff | `c906e153` | APPROVE, all four findings CLOSED |

The four document legs (PRD, TRD, TSD, personas) carry no change from this run: the batch
touched `scripts/`, `tools/` and the shipped doctrine only. `reference-doctrine.md` gained
rule 19, which is the sole spec-level change and is guarded by
`tools/doctrine_review_scope.py`.

## Verdict

**APPROVE.** Nine units delivered, every blocking finding repaired inside the batch that
caused it, and both repair sets confirmed by an independent pass that found nothing new. Both
suites green with exit codes captured directly rather than through a pipe.

## The finding that matters most

**A false claim shipped inside the epic built to catch false claims.** `US0577`'s changelog
fragment and its commit message both stated that `critic.py brief` emits a fingerprint. It did
not. `brief_fingerprint` had exactly one caller - the `--brief-file` branch of `record` - and
the command that ISSUES a brief never called it, so no command a reviewer could run produced
the value the gate demanded.

Its acceptance test passed throughout, because it computed `brief_fingerprint(critic.brief(
...))` in-process. That is a library test standing in for a lane test, and a library test
cannot see missing wiring: the wiring is precisely the part it does not exercise. Three of the
five EP0194 findings were this same shape.

This is the sprint's most valuable output, because it is general. It is now
`CR0520` (a `verify_ac lane-check` pass), a rule in `AGENTS.md` marked known-weak until that
lands, and a standing practice: every claim exercised through the shipped CLI in a throwaway
fixture before a reviewer is asked to look. Ten claims were checked that way before the final
two commits, and the confirmation passes then found nothing new.

## What the reviewers probed and found clean

- The widened coverage gate cannot be escaped by mislabelling: the tagger is the independent
  reviewer, `independence(reviewer, author)` runs on every path, and `conformance.py` keeps a
  per-unit REJECT blocking regardless of a batch-level pass.
- `_ensure_brief_column` migrates a pre-Brief log without disturbing the supersession section
  below the table, verified against the live log.
- The `claim_drift` repair is discrimination, not the lane switching off: each guard's mutant
  reddens its own test while the positive controls stay green, and both go red under a
  `return []` early exit.
- The disputed fixture change was settled empirically rather than argued - real `git diff`
  emits the context line the old fixture omitted, and the production `-U0` path supplies the
  funcname in the hunk header. Both are handled, so the fixture moved toward reality.
- The 40-commit replay reproduced exactly: before 215 findings / 135 empty, after 74 / 0.

## Disposition

Fifteen findings, all dispositioned in `RETRO0088`: eight repaired in-sprint
(`c906e153`, `a0e72a62`), seven filed (`BG0476`-`BG0478`, `BG0483`, `CR0518`-`CR0520`), none
declined. Nine further open findings carried with an explicit ruling, `BG0470` ruled with
executed evidence rather than judgement.

## The finding that outlives the batch

Two review rounds were needed on one batch, and the operator named the cost plainly: on a real
team, needing two or three reviews each time is verification handed to somebody else, and it
isolates the person doing it. The count is the signal, not the severity.

The repair is not resolve-to-be-careful. It is `CR0520`, which makes a criterion verified only
through the library visible mechanically, and the front-door check run before a reviewer is
engaged rather than after.

`CR0522` is filed from this close: the repo-wide periodic review blocked a sprint whose own
work was fully reviewed and signed off, and `--file-and-close` would not file it because the
lane is classified a correctness gate. A stale periodic ceremony is a cadence fact, not a
correctness fact about this batch.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | Claude Opus 5 | Closing review recorded for RUN-01KYY52D |
