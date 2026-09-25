# BG0704: The Done guard reads a filed closure naming the unit itself as a repair, and lists repaired findings as outstanding when the only APPROVE is the author's own

> **Status:** Superseded
> **Closes with:** US0914 (D0264: superseded only once it ships; backlog sweep D0265, sdlc-studio/reviews/backlog-sweep-2026-09-24.md)
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/conformance.py
> **Evidence:** Independent delivery review, RUN-01M2JA6J 2026-09-15: verdicts/US0627-delivery-engineering.txt (engineering seat); verdicts/US0627-delivery-qa.txt (qa seat); verdict rows in sdlc-studio/reviews/critic-verdicts.md. The second half is the implementer's observation during the US0627 repair, queued in findings/todo.txt. US0627 round-two delivery verdicts (qa brief da60784a5d19, engineering 5c7f8de69d59).
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

critic.py repair accepts a filed closure naming the unit itself, or any id that resolves such as a Done epic, and `coverage_state` reads that as repaired (critic.py:1427, the same at 3f73ab64). The delivered-terminal REJECT guard makes it a one-command route to Done: US0001 filed to US0001, then Done, exit 0. The ledger already holds BG0558 filed to BG0558, and no open bug or CR covers it. When every finding carries a closure but the only APPROVE is the author's own under the same brief, `repair_state` reads none and the refusal lists every finding as outstanding, which misdescribes what is missing. Checking filed ids on every read costs time in sweeps that open no corpus cache (critic.py:1782-1794): over 743 units `coverage_counts` went from 19.8 s to 28.6 s and whole-workspace conformance from 72.9 s to 76.3 s; gate.py and conformance open no cache window, and inside one the cost is zero. Round two of US0627 (4e780dcb) adds three: the close tail derives epics and requests over done and skipped units only (sprint.py:6674), so an epic whose last open child the run abandoned stays at Draft - safe, but no test pins it; the `_batch_unfanned_units` docstring's invariant 'never both and never neither' (sprint.py:6514) is stale now that abandoned units sit in a third list, `_batch_abandoned_units`; and the close's step-1 review-coverage still lists an abandoned unit that carries an unanswered REJECT.

## Steps to Reproduce

1. Record a delivery REJECT on US0001; python3 .claude/skills/sdlc-studio/scripts/critic.py repair --unit US0001 --closed '#1 -> filed: US0001'; transition.py set US0001 Done - exit 0. 2. Close every finding of a REJECT, then record an APPROVE by the unit's own author under the same brief; transition.py set <unit> Done - the refusal lists every finding as outstanding.

## Proposed Fix

Refuse a filed closure whose artefact is the unit itself or is not a bug, CR or story that can carry a finding. When every finding carries a closure and only a self-authored APPROVE follows, say that the missing piece is an independent APPROVE. Open one corpus cache around `coverage_counts` and the conformance sweep.

## Acceptance Criteria

The write-time check at critic.py:1515 asks one question - does the id resolve - and three
different wrong answers pass it. The criteria are asked at the write, because a closure refused
only at read time is already in an append-only ledger by the time anybody sees it.

### AC1: a `filed:` closure naming the unit under repair is refused

- **Given** US0001 carrying a live delivery REJECT with one itemised finding
- **When** `critic.py repair --unit US0001 --closed '#1 -> filed: US0001' --author '<author>'` runs
- **Then** it exits non-zero naming US0001 as the unit being repaired, the repair ledger is
  byte-identical before and after, `critic.coverage_state(US0001)` still reads `unreviewed` and
  `transition.py set US0001 Done` still refuses. The paired control, the same command filing to a
  bug that exists, is accepted and moves `coverage_state` to `repaired`
- **Mutant:** keep the resolves-only check at critic.py:1515 - the id resolves, so the repair is
  written, `repair_state` counts the finding closed, `coverage_state` reads `repaired` and the
  delivered-terminal guard passes: the one-command route to Done the ledger already holds for
  BG0558 filed to BG0558
- **Verify:** manual - retired by US0914: the `filed:` disposition went with `critic.py repair` and its ledger; a REJECT is answered only by a round-2 APPROVE from the reviewer who rejected, or carried at the review cap
- **Verified:** manual (2026-09-25) - retired, superseded by US0914

### AC2: a `filed:` closure must name an artefact that can carry a finding

- **Given** US0001 carrying a live delivery REJECT, and a Done epic on disk
- **When** `critic.py repair --unit US0001 --closed '#1 -> filed: EP0163' --author '<author>'` runs
- **Then** it exits non-zero naming the id's type and the types a finding can be filed to - a bug, a
  CR or a story, the types that carry acceptance criteria and a status a reader can follow - and
  writes nothing. Three controls are accepted on the same fixture: a bug, a CR and a story, so the
  refusal cannot be a blanket one
- **Mutant:** refuse only AC1's self-naming case, so every other resolving id still discharges the
  finding - a Done epic, an RFC or a retro, none of which can be worked, closes a review finding and
  the finding is never seen again
- **Verify:** manual - retired by US0914: the `filed:` disposition went with `critic.py repair` and its ledger; a REJECT is answered only by a round-2 APPROVE from the reviewer who rejected, or carried at the review cap
- **Verified:** manual (2026-09-25) - retired, superseded by US0914

### AC3: when every finding carries a closure, the refusal says an independent APPROVE is what is missing

- **Given** a unit whose delivery REJECT's every itemised finding carries a closure, followed by an
  APPROVE recorded by that unit's own author under the same brief
- **When** `transition.py set <unit> Done` runs
- **Then** it still refuses, because a self-authored APPROVE is not independent, and the detail
  states that every finding carries a closure and what is outstanding is an independent APPROVE,
  naming zero findings as outstanding. The control is a unit whose repair is genuinely partial,
  whose refusal still lists the findings that carry no closure
- **Mutant:** leave the `elif repair["state"] == "none"` branch at transition.py:1060-1062 reading
  `repair_state` as none once the later APPROVE has retired the rejection, so the refusal lists
  every finding as outstanding and sends the operator to `critic.py repair` for closures that are
  already in the ledger
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RejectNeedsAnAnswerTests::test_a_self_authored_approve_is_named_as_the_missing_half

### AC4: the filed-id check is paid once per sweep, not once per unit

- **Given** a workspace of many units whose repairs carry `filed:` closures, and a caller holding no
  corpus cache open
- **When** `critic.coverage_counts` over a batch and `conformance.detect_conformance` over the whole
  workspace each run
- **Then** every `sdlc_md.find_by_id` call made by `_closure_still_resolves` (critic.py:1800-1803)
  happens with `sdlc_md.corpus_cache_active()` true, from one window opened per sweep - asserted by
  recording the flag at each resolution rather than by timing, which is the measurement this repair
  cannot make deterministic
- **Mutant:** open the window inside `coverage_state` per unit, which builds and discards the memo
  once per unit and reproduces the measured cost the summary records (19.8 s to 28.6 s over 743
  units), or leave both sweeps uncached as they are today
- **Verify:** manual - retired by US0914: resolving a filed closure's id went with `critic.py repair` and its ledger; a REJECT is answered only by a round-2 APPROVE from the reviewer who rejected, or carried at the review cap
- **Verified:** manual (2026-09-25) - retired, superseded by US0914

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
| 2026-09-17 | sdlc-studio | Groomed for `sprint plan`: the two derived criteria are replaced by four authored ones - the self-naming filed closure, a closure filed to a type that carries no finding, the refusal that misdescribes a self-authored APPROVE as outstanding findings, and one corpus window per sweep. The three round-two observations the summary records (the close tail's epic derivation over abandoned units, the stale `_batch_unfanned_units` docstring, and step-1 review coverage listing an abandoned unit) are not covered by these criteria and remain unfiled work. AC4's second sweep lives in `conformance.py`, which `Affects` does not yet name - add it before delivery, or the review's bounded scope will not reach the change. |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): held open under D0264 until US0914 ships - planning: SUPERSEDED - Done guard reading repair closures: repair ledger deleted in batch 2; superseded only once US0914 ships (D0264) |
| 2026-09-25 | Claude Opus 5.5 | AC1, AC2, AC4 retired by US0914 (D0259 pattern): `critic.py repair` and its ledger were deleted, so a REJECT is answered only by a round-2 APPROVE or carried at the cap |
| 2026-09-25 | sdlc | Superseded under D0273: US0914 is Done and retired critic.py repair and the repair ledger this bug describes |
