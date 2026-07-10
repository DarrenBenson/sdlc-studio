# CR-0212: eval run: a deterministic runner for the two-Claude eval gate

> **Status:** In Progress
> **Verification depth:** functional (red-then-green: setup builds a fixture from the machine spec + prints the worker prompt, prose-only scenarios degrade honestly rc 1, record rejects unknown behaviours, report gates on blocking failures AND ungraded blocking behaviours; live smoke against scenario 05 e2e; scenarios 05/06 carry executable fixture specs; release-gate + evals/README point at the runner; tools suite 130)
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

The eval gate is mandated (release-gate template, rc checklist, epic close) but wholly untooled: running it means hand-building fixture repos from each scenario's prose setup, hand-spawning a worker, hand-grading against `expected_behaviours`, and hand-recording the outcome. Done three times this sprint, each time improvised. A first-time operator cannot run the gate the docs require of them.

## Acceptance Criteria

- [ ] `eval_run.py` builds each scenario's fixture from a machine-readable setup block, emits the worker prompt, and records the graded verdict per expected behaviour
- [ ] Scenario JSON gains a structured fixture spec (files + config) so setup is executable, not prose
- [ ] The release-gate and epic-close docs point at the runner instead of describing a manual ceremony

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Raised |
