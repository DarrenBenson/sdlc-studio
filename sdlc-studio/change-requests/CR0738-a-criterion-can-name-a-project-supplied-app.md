# CR-0738: A criterion can name a project-supplied app command, and the review records the evidence it produced

> **Status:** In Progress
> **Decomposed-into:** EP0375
> **Parent:** RFC0067
> **Priority:** Low
> **Type:** Feature
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/reference-verify.md, tools/tests/test_verify_app_evidence.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** spawned by RFC0067, ruled 2026-11-17
> **Date:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T21:40:06Z

## Summary

Executable criteria run tests. Nothing lets a criterion say drive the built application and show me, so a unit can pass with every test green and a screen that does not render. RFC0067 ruled this orchestrate-only: a `Verify: app <command>` line runs a command the project supplies, `verify_ac` records its exit code and the paths of any files it wrote under a declared evidence folder, and the reviewer's brief lists them. The skill ships no browser driver.

## Impact

Projects with a user interface, whose reviews today cannot see the running product.

## Acceptance Criteria

- [ ] `verify_ac` runs a `Verify: app <command>` line, passes on exit 0, and records the files the command wrote under the declared evidence folder
- [ ] A command that exits 0 and writes no evidence fails the criterion, naming the folder it looked in
- [ ] `critic.py brief` lists the recorded evidence paths for the unit, and lists none without failing when the unit has no app criterion

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Raised |
