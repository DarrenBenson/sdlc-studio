# CR-0301: report.enabled=false gates only the text page - --format json bypasses the switch undocumented and untested, and the notice claims rendering is disabled outright

> **Status:** In Progress
> **Decomposed-into:** EP0074
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, sdlc-studio/stories/US0176-report-rendering-gated-by-config-while-measurement-is.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

`sprint_report.py`:149's `if not rendering_enabled(root) and args.format != "json":` means a project that set report.enabled: false still gets the complete composed report via `show --format json`. Two audit lenses filed this independently; panels split 4 not-refuted / 2 refuted, the refuters arguing the exemption matches the module's page-vs-data philosophy (`rendering_enabled`'s docstring gates 'whether the report PAGE is drawn'). Triaged as a CR rather than a bug accordingly: the design intent is defensible but recorded nowhere - the printed notice says 'rendering disabled', not 'text rendering disabled; json data remains available'; US0176 AC1 and ConfigGateTests exercise only format="text" (LL0013); reference-scripts-domain.md describes an unconditional gate. Whichever intent is real, it needs stating and testing so the Done story's AC distinguishes the two.

## Impact

`sprint_report.py`:149's `if not rendering_enabled(root) and args.format != "json":` means a project that set report.enabled: false still gets the complete composed report via `show --format json`.

## Acceptance Criteria

- [ ] The json exemption is either removed (gate covers both formats) or documented as page-vs-data in the code comment, `rendering_enabled` docstring, the disabled notice text, and reference-scripts-domain.md
- [ ] A ConfigGateTest covers the json path against a disabled config, asserting whichever behaviour was chosen

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Raised |
