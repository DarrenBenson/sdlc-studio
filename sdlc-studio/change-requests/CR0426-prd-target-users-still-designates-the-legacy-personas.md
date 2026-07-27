# CR-0426: PRD Target Users still designates the legacy personas.md four, contradicting the Cooper registry's declared Primary

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** sdlc-studio/prd.md
> **Date:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

The top-of-pipeline authority answers 'who is this for' with the four legacy role-personas and points at personas.md, while personas/index.md declares Maya Okafor Primary, Jonah secondary, Trevor negative; the PRD never mentions any of them, so the two persona systems give contradictory design targets and RV0010's '`referenced_in_prd`: []' finding remains true.

## Impact

The top-of-pipeline authority answers 'who is this for' with the four legacy role-personas and points at personas.md, while personas/index.md declares Maya Okafor Primary, Jonah secondary, Trevor negative; the PRD never mentions any of them, so the two persona systems give contradictory design targets and RV0010's '`referenced_in_prd`: []' finding remains true.

## Acceptance Criteria

- [ ] Rewrite the PRD Target Users section to name the registry's Primary/Secondary/negative personas with a pointer to personas/index.md, and demote personas.md to an explicitly-labelled legacy appendix (or fold its still-true content into the registry).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Raised |
