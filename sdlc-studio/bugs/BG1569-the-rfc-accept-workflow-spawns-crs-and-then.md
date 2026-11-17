# BG1569: The RFC accept workflow spawns CRs and then sets Accepted, which the transition gate refuses

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/reference-rfc.md, .claude/skills/sdlc-studio/help/rfc.md
> **Evidence:** accepting RFC0065 and RFC0066 on 2026-11-17; the refusal transition.py printed, against reference-rfc.md section accept steps 3 and 4
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T17:27:17Z

## Summary

reference-rfc.md tells the operator to spawn the workstream CRs and then set the RFC to Accepted, and says Accepted is not terminal. transition.py treats Accepted as a terminal derived from the children and refuses it while any spawned CR is unresolved, which is always the case at the moment the workflow reaches that step. The only way through is --force, so every accepted RFC with spawned CRs has been accepted by override, and the documented happy path cannot be followed as written.

## Steps to Reproduce

1. Resolve every open decision on a Draft RFC with rfc.py resolve.
2. Spawn a CR with `file_finding.py` and the RFC as parent, as the accept workflow says.
3. Run transition.py set with the RFC id and Accepted.
4. It is blocked: the status is derived from its children and the new CR is Proposed.
5. The same command with --force succeeds.

## Proposed Fix

Decide which is right and make the two agree: either Accepted is the decided state an RFC enters when its decisions are resolved, with the derived gate moved to a later closed status, or the workflow in reference-rfc.md names the status an RFC holds between decision and delivery. Pin it with a test that follows the documented accept steps without --force.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: reference-rfc.md tells the operator to spawn the workstream CRs and then set the RFC to Accepted, and says Accepted is not terminal.
- [ ] **AC2** The proposed fix lands, pinned by a test: Decide which is right and make the two agree: either Accepted is the decided state an RFC enters when its decisions are resolved, with the derived gate moved...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
