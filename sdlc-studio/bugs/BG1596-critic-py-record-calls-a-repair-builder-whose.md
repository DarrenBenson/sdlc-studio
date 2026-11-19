# BG1596: critic.py record calls a repair builder whose prompt names the verdict path the agent 'briefed with' the verdict, and reports the verdict's provenance as unknown

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/lib/verdict_provenance.py, changelog.d/BG1596.md
> **Evidence:** critic.py record --unit US1316, 2026-11-18.
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T16:20:16Z

## Summary

Recording US1316's REJECT printed 'US1316's verdict file provenance is unknown: agent a77dab0c350fa2fb0, briefed with it, never wrote it, and agent a7c45cbd1b07074f1 last wrote it'. a77dab0c350fa2fb0 is the repair builder, whose prompt named the verdict file to read; the reviewer a7c45cbd1b07074f1 wrote it. Provenance reads any agent whose prompt holds the verdict path as the briefed reviewer.

## Steps to Reproduce

Name a verdict file's path in a repair builder's prompt, then `critic.py record` that verdict: it reports the repair builder as briefed with it and the provenance as unknown.

## Proposed Fix

Attribute a verdict to the agent whose prompt carries its review brief (the BRIEF line or the brief file), not to every agent whose prompt mentions the verdict path.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Recording US1316's REJECT printed 'US1316's verdict file provenance is unknown: agent a77dab0c350fa2fb0, briefed with it, never wrote it, and agent...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Name a verdict file's path in a repair builder's prompt, then `critic.py record` that verdict: it reports the repair builder as briefed with it and the...
- [ ] **AC3** The proposed fix lands, pinned by a test: Attribute a verdict to the agent whose prompt carries its review brief (the BRIEF line or the brief file), not to every agent whose prompt mentions the verdict...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
