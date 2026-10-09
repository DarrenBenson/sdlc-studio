# CR-0616: verify_ac should record a red baseline: a Verify that already passes before the story is implemented cannot tell done from not-done

> **Status:** In Progress
> **Consulted:** Dani Okafor, Lena Marsh, Sam Eriksson (2026-10-09)
> **Decomposed-into:** EP0281
> **Priority:** Medium
> **Type:** Feature
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/reference-verify.md, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Evidence:** homelab US0188 AC1 (sdlc-studio/stories/US0188-*.md revision 2026-10-07); related but distinct: BG0014 (source-grep Verify lines), BG0193 (a test filter matching nothing)
> **Date:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T14:35:23Z

## Summary

TDD is the doctrine (author the Verify first, then make it pass), but nothing checks that a story's Verify expression was ever RED. A Verify that passes at planning time is green whether or not the story is delivered. Observed in the homelab consuming project (US0188 AC1, 2026-10-07): `Verify: shell grep -q drift-check utilities/monitoring/ab01-openclaw-monitoring.cron` was meant to prove the drift check was scheduled, but the file's HEADER COMMENTS already mentioned drift-check.py since an earlier story, so the AC was green before a line of US0188 existed and would have stayed green had the schedule never been added. It was caught by the author re-reading the AC, not by any tool. Proposal: `verify_ac.py baseline --id US....` (or an automatic baseline on the transition into In Progress) runs each executable Verify and records `Baseline: pass|fail (date)` beside it; `transition -> Review/Done` warns (configurable to refuse) on any AC whose baseline was `pass` and whose Verify text has not changed since - 'this AC was already green before you started'. A `manual` AC and an AC explicitly marked as a regression guard (`Baseline-expected: pass`) are exempt.

## Acceptance Criteria

- [ ] `verify_ac.py baseline --id <unit>` runs each executable Verify and records its result beside it as a dated baseline
- [ ] A transition to Review or Done warns, configurably refuses, on a criterion whose baseline passed and whose Verify text has not changed since
- [ ] A `manual` criterion, and one marked as a regression guard expected to pass at baseline, is exempt

## Triage

- Affects paths corrected to repository paths (they were filed relative to the skill). Criteria added for refinement from the proposal in the Summary. Related, not duplicates: BG0014, BG0193.
- A design change to the delivery loop, sized at refinement; under LL0056 it should say which check it retires or why none.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | sdlc-studio | Raised |
| 2026-10-07 | Claude Opus 5.5 (triage) | Triaged: Affects paths corrected; criteria added; related bugs named |

## Amigo Consult

_Consulted 2026-10-09: Dani Okafor (engineering, lead), Lena Marsh (product), Sam Eriksson (qa). Settle before building._

- Rule 21: should the operator reverse it for the revert, while mutation stays on demand? The panel says not on today's evidence: the yield is unaudited or relayed, and zero on this repository's sample. It recommends ruling after the yield count above. The drafter agrees.
- What should `review.revert_check` default to, if the gate is ruled in? Product and engineering recommend shipping `report`, with this repository's own config at `block`. That serves Jonah's End goals 2 and 4, and line coverage already ships `off`. QA prefers `block` everywhere. This draft carries `report`, with `block` here.
- Dry runs: the panel's reading is that 'not previewed' predicts no pass, so it keeps the ladder's rule that a preflight never predicts a write the real run refuses. It departs from the ladder's literal practice of running every gate on a dry run. Does the operator agree?
- Should the review brief print the revert verdict, and drop the reviewer's hand revert (the step behind BG0604), as a follow-up after G6 and G10? Until then the gate retires nothing. The cheap 6.2 step is G12 Q6: the brief prints the revert-check command for every unit with a base.
