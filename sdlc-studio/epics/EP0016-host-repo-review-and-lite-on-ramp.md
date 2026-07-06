# EP0016: Host-repo review and lite on-ramp

> **Status:** Draft
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new

## Summary

The adoption on-ramps: a first-class `review generate` command that runs an architectural,
code-quality and defensive-security review of the host repo and triages findings (the
lowest-commitment way to try the tool on existing code - dogfooded as RV0006 this session),
and a lite profile that collapses the pipeline to PRD/story/implement for small repos so the
discipline survives without the ceremony. Groups CR0175 (review command), CR0176 (lite
profile). Independent of the schema work; CR0175's security wording is load-bearing for
frontier-model runnability and must ship verbatim.

## Story Breakdown

- [x] [US0070: review generate command with remediation-only security posture](../stories/US0070-review-generate-command-with-remediation-only-security-posture.md)
- [ ] [US0071: Lite profile collapsing the pipeline to PRD, story, implement](../stories/US0071-lite-profile-collapsing-the-pipeline-to-prd-story.md)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
