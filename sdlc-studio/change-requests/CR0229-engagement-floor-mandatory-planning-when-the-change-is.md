# CR-0229: engagement floor: mandatory planning when the change is multi-file in a spec-bearing repo

> **Status:** Deferred
> **Target:** v4.1
> **Priority:** High
> **Type:** Improvement
> **Date:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

The v4 benchmark rerun (docs/benchmarks/2026-07-10-v4-rerun.md, finding 3) showed the scale-to-size judgement failing model-dependently: every Sonnet and Opus pipeline-arm agent judged a multi-file, spec-interacting ticket too small for ceremony and shipped the hidden-requirement defect the ceremony catches, while frontier-model agents engaged unprompted. The engagement threshold must not be left to the weaker model's own judgement. Ship a deterministic engagement floor: when a change touches more than one source file in a repo carrying a numbered spec (or sdlc-studio workspace), the planning/AC pass is mandatory, not advisory - a small, checkable rule in the doctrine and agent-instructions template, with an explicit config opt-out for operators who accept the risk.

## Acceptance Criteria

- [ ] The doctrine and the shipped agent-instructions template state the floor as a hard rule (multi-file + spec-bearing repo -> mandatory spec-delta/AC pass before code), with the config opt-out named
- [ ] The floor is mechanically checkable where an sdlc-studio workspace exists (gate or conformance refuses a Done multi-file unit with no plan/AC artefact), advisory prose elsewhere
- [ ] A future protocol revision measures the floor as its own benchmark arm (noted in protocol docs; not a blocking AC for this CR)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Raised |
