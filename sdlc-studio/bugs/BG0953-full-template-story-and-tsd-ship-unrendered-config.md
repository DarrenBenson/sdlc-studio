# BG0953: Full-template story and TSD ship unrendered {{config.story_quality.*}} placeholders

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/templates/core/story.md, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
> **Evidence:** Reproduced 2026-10-06 in a scratch project with skill 6.1.0+12 (aa19a2e3); observed in homelab US0230 promote
> **Created:** 2026-10-06
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-06T12:35:53Z

## Summary

`artifact.py new --type story --template full` and `artifact.py promote --id <id> --to full` both write the two quality-floor lines from templates/core/story.md verbatim: `> **Minimum edge cases:** {{config.story_quality.edge_cases.api}} for API stories, {{config.story_quality.edge_cases.other}} for others` and the matching test-scenarios line. The values exist in templates/config-defaults.yaml (`story_quality)` and the project config, but nothing substitutes `{{config.*}}` keys, so every full story carries two lines the author must hand-delete, and the floor the line exists to state is never shown. templates/core/tsd.md uses the same syntax. Seen live in homelab on 2026-10-06 promoting US0230.

## Steps to Reproduce

1. init a scratch project; create an epic
2. artifact.py new --type story --title X --epic <EP> --template full
3. grep -c '{{config\.' on the story -> 2
4. Same after artifact.py promote --id <planning story> --to full -> 2

## Proposed Fix

Resolve `{{config.<dotted.key>}}` from the merged project config (config-defaults.yaml + .config.yaml, via `sdlc_md.project_override)` when rendering full templates and promote scaffolds; leave unknown keys as-is and test both paths. Alternatively drop the line from the scaffold and let the quality gate state the floor.

## Acceptance Criteria

- [ ] **AC1** A story written by `artifact.py new --type story --template full` contains no `{{config.` token and no `Minimum edge cases` or `Minimum test scenarios` line
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py -k full_story_no_config_token
- [ ] **AC2** The same holds for a planning story raised by `artifact.py promote --id <id> --to full`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py -k promote_no_config_token
- [ ] **AC3** reference-config.md no longer names the story template as a reader of `story_quality.edge_cases.api` or `story_quality.test_scenarios.api`
  - **Verify:** manual - two Used In cells in a reference table; read them

## Triage

- Scoped to the story scaffold. A TSD is authored through the `tsd` workflow, not written by
  `artifact.py`, so its `{{config.coverage.*}}` slots are filled by the author like any other
  placeholder; tsd.md leaves Affects.
- Operator ruling 2026-10-06: drop the two lines rather than render them. No script reads
  `story_quality.edge_cases` or `story_quality.test_scenarios` (only `story_quality.sizing`, in
  route.py), so a rendered floor would state a number no gate enforces. `artifact.py` reads the
  template, so it needs no change. The agent checklists in reference-outputs.md that cite these
  keys are guidance an agent resolves from config, and stay.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-06 | sdlc-studio | Filed |
| 2026-10-06 | Claude Opus 5.5 (triage) | Groomed: tool-derived criteria replaced with checkable ones; scoped to the story scaffold, tsd.md out of Affects |
| 2026-10-06 | Claude Opus 5.5 (triage) | Re-groomed on the operator's ruling to drop the lines: 2 -> 1 point; Affects swaps artifact.py for reference-config.md; AC3 added |
