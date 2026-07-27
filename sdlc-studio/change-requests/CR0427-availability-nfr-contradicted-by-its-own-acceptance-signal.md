# CR-0427: Availability NFR contradicted by its own acceptance signal: PRD says sync 'degrades gracefully', TSD proves it aborts wi

> **Status:** In Progress
> **Decomposed-into:** EP0168
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** sdlc-studio/prd.md
> **Date:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

The PRD requires sync to degrade gracefully when gh/remotes are absent while the TSD's NFR-mapping row for the same requirement asserts the opposite as tested behaviour (abort with exit 127, 'does not degrade gracefully'), so the requirement as written is untestable against the acceptance signal that exists: the test that would satisfy the PRD would fail today.

## Impact

The PRD requires sync to degrade gracefully when gh/remotes are absent while the TSD's NFR-mapping row for the same requirement asserts the opposite as tested behaviour (abort with exit 127, 'does not degrade gracefully'), so the requirement as written is untestable against the acceptance signal that exists: the test that would satisfy the PRD would fail today.

## Acceptance Criteria

- [ ] Decide the requirement: either reword the PRD Availability clause to match the shipped fail-loud contract (offline pipeline degrades; `github_sync` aborts cleanly), or keep graceful degradation as the requirement and file the work to implement it - then make both documents state the same behaviour.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Raised |
