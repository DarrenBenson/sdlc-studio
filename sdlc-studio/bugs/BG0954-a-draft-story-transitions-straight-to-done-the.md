# BG0954: A Draft story transitions straight to Done - the Definition of Ready is never required

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Evidence:** Reproduced 2026-10-06 in a scratch project with skill 6.1.0+12 (aa19a2e3); homelab US0230 Draft -> Done the same day
> **Created:** 2026-10-06
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-06T12:35:56Z

## Summary

`transition.py set --id <story> --status Done` moves a story from Draft to Done when its Done gates are green (verify report, open questions, template tier); no gate asks whether it was ever Ready. reference-outputs.md documents Draft -> Ready -> Planned -> In Progress -> Review -> Done, and even the compressed agentic flow keeps Draft -> Ready -> Done (Draft -> Done is documented only for epics in batch mode), while reference-story.md checks Ready only at implement. So a story can be authored, verified and closed without ever passing the Definition of Ready, and `requirements` reports 'no unmet requirements' for it. Seen live in homelab on 2026-10-06: US0230 went Draft -> Done.

## Steps to Reproduce

1. init a scratch project; epic + story (--template full)
2. Fill placeholders, set every AC to `Verify: shell true`, resolve open questions
3. `verify_ac.py` run --id <story> -> pass=3
4. transition.py requirements --id <story> --status Done -> 'no unmet requirements'
5. transition.py set --id <story> --status Done -> 'Draft -> Done', file says Done

## Proposed Fix

In transition(), refuse a story moving from Draft (or Proposed) to a delivered terminal status unless the Definition of Ready passes or the story records a reason (the same sanctioned-skip-with-reason pattern the Done guard already uses); surface it in `requirements`. Won't Implement / Deferred / Superseded stay reachable from Draft. Add the case to the transition tests.

## Acceptance Criteria

- [ ] **AC1** A Draft or Proposed story that misses a Definition of Ready check `sprint plan` applies (resolvable `Affects`, `Points` on the scale) is refused by `transition.py set --status Done`, naming the unmet item, even with green executable criteria; the same story with the item met goes through
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k draft_to_done_requires_ready
- [ ] **AC2** `transition.py requirements --id <story> --status Done` lists that unmet item for the same Draft story
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k requirements_names_ready
- [ ] **AC3** A recorded `> **Decision-Override:**` reason lets the move through and is reported, and `Won't Implement` and `Superseded` stay reachable from Draft without the check
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k draft_closures_unaffected

## Triage

- The documented contract already says Draft -> Ready -> Done, even in the compressed agentic
  flow (reference-outputs.md#compressed-status-flow). The Definition of Ready is gated only in
  `sprint plan`, so a story closed outside a sprint never meets it. The fix applies the existing
  deterministic checks at the second entry point; it adds no new rule.
- Operator ruling 2026-10-06: enforce Ready at the transition, not correct the docs to accept
  Draft -> Done outside a sprint.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-06 | sdlc-studio | Filed |
| 2026-10-06 | Claude Opus 5.5 (triage) | Groomed: tool-derived criteria replaced; scoped to the DoR checks `sprint plan` already runs, from Draft or Proposed only |
