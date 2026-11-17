# CR-0726: Retire or rewire the three unreferenced persona prompt templates that teach the pre-Cooper persona model

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/templates/personas/prompts/code-analysis-prompt.md, .claude/skills/sdlc-studio/templates/personas/prompts/discovery-presentation.md, .claude/skills/sdlc-studio/templates/personas/prompts/enrichment-questions.md, .claude/skills/sdlc-studio/reference-persona-generate.md, tools/tests/test_persona_templates_referenced.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, personas lens, survived 3 of 3 refute votes; observed at .claude/skills/sdlc-studio/templates/personas/prompts/enrichment-questions.md Whole directory: code-analysis-prompt.md (136 lines), discovery-presentation.md (67), enrichment-questions.md (197)
> **Date:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:29:12Z

## Summary

The directory templates/personas/prompts/ in the shipped skill holds three prompt templates, 400 lines in all: code-analysis-prompt.md, discovery-presentation.md and enrichment-questions.md. No script, reference page or help page names the directory or any of the three files, and their only change since v1.4.0 is a markdownlint sweep. Their content contradicts the current persona model: enrichment-questions.md classifies a persona as Team to be assigned to an amigo and asks for a representative quote, personality traits and a backstory incident, with no Cast role and no End Goals, while persona-template.md requires both and seats are resolved separately by declared role. An agent that finds the directory follows a retired model, and one that does not find it never uses it, so every install carries dead weight that can only mislead.

## Impact

Anyone running persona generation in a consuming project, and any agent that browses the templates tree, can pick up prompts that produce cards the current persona template and persona review would reject. Every install also ships 400 lines nothing loads.

## Acceptance Criteria

- [ ] Each of the three files is either removed from the shipped skill or named by reference-persona-generate.md as the prompt it loads for a stated step
- [ ] Any file that is kept asks for a Cast role and End Goals and no longer classifies a persona as Team to be assigned to an amigo, in agreement with persona-template.md
- [ ] A test in tools/tests/`test_persona_templates_referenced.py` fails when a file under templates/personas/ is named by no shipped reference page, help page or script

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Raised |
