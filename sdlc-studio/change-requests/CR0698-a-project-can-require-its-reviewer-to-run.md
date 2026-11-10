# CR-0698: A project can require its reviewer to run on a different model family or harness from the builder, and each verdict records the reviewer's model

> **Status:** Proposed
> **Priority:** Medium
> **Type:** enhancement
> **Size:** M
> **Related:** EP0280, CR0667, RFC0063, RFC0064
> **Date:** 2026-11-10
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson (operator); human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-10T17:24:58Z

## Summary

Review independence today is a fresh context that did not write the code: critic.py refuses a reviewer id equal to the author's, `routing.critic_tier` keeps the critic at least the author's size, and sprint sign refuses a principal who authored or reviewed a unit. EP0280 (run ten) binds each verdict to the agent that wrote it and names a verdict from the editing context a self-review. Nothing lets a project require the reviewer to be a different model family or harness, and a verdict does not record the reviewer's model, so the question cannot be measured.

Two consuming projects' agents raised it on 2026-11-10: a review by the same model family over the same state is closer to a self-check. Both said it is opinion, not measured. A lane can already run headless in another CLI harness (CR0667), so a cross-family reviewer is possible by hand; this makes it a setting and makes its yield visible.

## Impact

Serves Graham Doyle's End goal 2 (trust that the evidence came from the process) and O10. Opt-in, never a default gate: its yield is read from the model scorecard (RFC0063 WS6) and RFC0064's change failure rate.

## Acceptance Criteria

- [ ] Each recorded verdict states the reviewer's model and harness where the harness's store gives them, and 'unknown' where it does not
- [ ] A project can set `review.reviewer_family: different` (default `any`); with it set, `critic.py record` refuses a verdict whose reviewer model family matches the builder's, naming both, and accepts one whose family is unknown only with a recorded waiver
- [ ] `critic.py brief` names the harness and model to dispatch the reviewer to when the setting is on, using CR0667's headless lanes
- [ ] The sprint report states, per reviewer model family, the reviews done, rejections upheld and escapes later traced to them, so the setting's yield is read rather than assumed

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-10 | Darren Benson (operator) | Raised |
