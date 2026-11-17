# CR-0737: Generate mode reads schema dumps, stored-procedure source and trace exports from a declared folder

> **Status:** In Progress
> **Decomposed-into:** EP0374
> **Parent:** RFC0067
> **Priority:** Low
> **Type:** Feature
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/reference-prd.md, .claude/skills/sdlc-studio/reference-trd.md, .claude/skills/sdlc-studio/help/brownfield-runbook.md, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, tools/tests/test_generate_runtime_inputs.py
> **Evidence:** spawned by RFC0067, ruled 2026-11-17
> **Date:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T21:40:05Z

## Summary

`prd generate` and `trd generate` reverse-engineer a spec from source files. Business rules held in a database schema, a stored procedure or only visible in a trace are missed unless they happen to sit in the repository. RFC0067 ruled that such inputs are files: a project declares a folder, places exports in it, and generate mode lists what it read and cites those files as evidence. The skill never connects to a running system.

## Impact

Teams reverse-engineering a system whose logic lives partly in its database; their generated spec is silently incomplete today.

## Acceptance Criteria

- [ ] A `generate.runtime_inputs` setting names a folder, and the PRD and TRD generate workflows instruct the agent to read it and to cite each file it drew a requirement from
- [ ] The workflows state that the skill reads exports only and never connects to a database or a running service
- [ ] The brownfield runbook says what to export and where to put it

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Raised |
