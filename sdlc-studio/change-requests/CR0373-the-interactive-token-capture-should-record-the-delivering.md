# CR-0373: the interactive token capture should record the delivering model so the velocity row lands in the right (project, model) cell

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py
> **Date:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

US0279's close-time capture reads the harness transcript for the token total, but not the model that spent them, so an interactive sprint's velocity row books under the unrecorded-model cell. The rate machinery already segments per (project, model) and refuses pooling - an Opus tokens-per-point and a Fable tokens-per-point are different currencies - so the operator's cross-model calibration question (observed: Opus roughly 1M tokens and 1 hour per 20 points; Fable roughly 2 hours, tokens uncalibrated) cannot be answered from interactive rows until the model is on them. The transcript records the model per message beside the usage the capture already sums.

## Impact

every interactive sprint on a non-default model; without it the per-model rate the planner reads stays a runner-only measurement

## Acceptance Criteria

- [ ] `harness_tokens` also returns the model(s) seen in the session transcript, mixed reported as mixed
- [ ] the velocity row written by an interactive close carries that model in its Model cell, so `measured_rate` books it in the right (project, model) cell

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Raised |
