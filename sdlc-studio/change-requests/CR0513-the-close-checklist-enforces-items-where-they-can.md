# CR-0513: The close checklist enforces items where they can still be satisfied, reads verdicts rather than counts, and checks how a review was briefed

> **Status:** Complete
> **Decomposed-into:** EP0197
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/decisions.py
> **Priority:** High
> **Type:** Improvement
> **Size:** L

## Summary

The compulsory checklist certifies that a review HAPPENED. It cannot tell whether the review was conducted properly, and two of its items can only be answered at a moment when answering them is already impossible. Measured on RUN-01KYX375, where all three blocking items resolved to a waiver or a blind pass.

FLAW 1 - ITEMS FIRE AFTER THEIR WINDOW HAS CLOSED. `goal-seat-reviewed` can only be satisfied before the plan is written; `batch-boundary-review` only while a delivery batch is open. Both are evaluated at the close, when neither can be done. The waiver is therefore not a decision but the only available exit, and both of this run's waivers say so in terms ('the run is over and a span cannot be opened retrospectively'). A gate whose only possible outcome at firing time is a waiver is a receipt, not a gate.

FLAW 2 - VERDICT-BLINDNESS. `_ck_closing_review` returns RAN on `len(reviews)` and `len(rounds)` and never reads a verdict. This run recorded four rounds of which THREE were REJECT, and the item reported `[ran] 71 recorded pass(es), 4 round(s)`. That is the same class as BG0441, which laundered a per-unit REJECT into coverage - repaired in `review_coverage` and still live here. `signoff` likewise reports `1/37` as `[ran]`.

FLAW 3 - NO PROVENANCE. Nothing checks HOW the review was briefed. Every process failure of this run was invisible to all eighteen items: review prompts hand-written instead of taken from `critic.py brief`; seats chosen by judgement instead of `persona_resolve.py panel`; reviewers instructed to 'default to REJECT'; a base ref two weeks stale (BG0470); findings never classified regression against pre-existing; and two acceptance criteria ticked which `git diff` disproves.

FLAW 4 - INTERNAL CONTRADICTION. One close reported three different answers to one question - `9/9 units covered` (chain step 1), `0 covered, 0 rejected, 37 uncovered` (item 15), and `71 recorded pass(es)` (item 6) - because they compute over different unit sets. Nothing noticed.

## Impact

The checklist is the last thing standing between a sprint and a signed-off close, and it currently passes a run in which the reviews were conducted wrongly, rejected three times out of four, and covered one unit in thirty-seven for sign-off. An operator reading `[ran]` beside `Closing full-diff review` has been told the opposite of what happened.

This makes closes CHEAPER, not dearer. Two of the three items that blocked this close cost a waiver each precisely because they were raised too late; enforced at plan and at commit they cost seconds and the fix is free. The new items are DERIVED from the tree rather than asked, so they add no questions for a human to answer.

## Acceptance Criteria

- [ ] Every checklist item declares its enforcing command, and an item whose window closes before the close is enforced there - proven by a test in which skipping the goal review fails `sprint plan --write` rather than surfacing at the close
- [ ] A run whose only recorded review verdicts are REJECT reports the closing-review item as OUTSTANDING, not `[ran]` - the positive control being that an APPROVE covering every unit passes
- [ ] A verdict whose brief did not come from `critic.py brief` is detected and reported, proven by recording one hand-written verdict and one tool-briefed verdict and asserting they resolve differently
- [ ] A unit whose ticked criteria the tree contradicts is reported OUTSTANDING, proven against a unit whose story file is byte-identical to the base ref while its criteria are ticked
- [ ] A waiver records its kind, and a window-expired waiver is counted separately in the retro from a deliberate one
- [ ] Two checklist rows cannot report different answers to the same coverage question; a disagreement is itself an outstanding item
- [ ] Replayed against RUN-01KYX375, the checklist reports the three items this run passed or waived as outstanding, and the measured before/after is recorded rather than asserted

## Proposed Fix

1. WINDOWS. Every item declares the last command by which it can still be satisfied, and THAT command enforces it. `goal-seat-reviewed` is enforced by `sprint plan --write` - `--skip-personas` must record its waiver at that moment, with an authoriser, rather than being noticed at the close. `batch-boundary-review` is enforced when a delivery commit lands with the run open and no span. The close then REPORTS these rather than gating on them, because it cannot fix them.
2. VERDICTS, NOT COUNTS. A review item resolves from the verdict: an APPROVE covering each unit passes; a REJECT with no later APPROVE is OUTSTANDING, never `[ran]`. Same rule for sign-off coverage.
3. PROVENANCE ITEMS, all machine-checkable: every recorded verdict carries the brief hash `critic.py brief` emitted, so a hand-written prompt is detectable; every verdict names a seat `persona_resolve` recognises; every finding carries a REGRESSION / NEW / PRE-EXISTING classification (CR0512); the base ref used post-dates the run's own `started_at` (BG0470).
4. TICKS AGAINST THE TREE. A unit whose criteria are ticked is re-verified, and a tick the tree contradicts is OUTSTANDING. Two of this run's units were rejected for exactly this and the checklist passed them.
5. WAIVER KINDS. A waiver records whether the item was deliberately set aside or was already unsatisfiable when it fired. The second is a process failure to be counted, not a decision to be respected, and the retro should report how many items expired before anyone was asked.
6. ONE NUMBER. Coverage is computed once and read by every consumer; two rows disagreeing about the same question is itself OUTSTANDING.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
