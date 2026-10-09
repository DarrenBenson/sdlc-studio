# BG1020: transition.py refuses an RFC's Accepted until its spawned CRs are resolved, contradicting reference-rfc.md's accept step

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/reference-rfc.md, .claude/skills/sdlc-studio/scripts/tests/test_rfc_accept_with_open_children.py, changelog.d/BG1020.md, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Evidence:** transition.py:1060 `_request_terminal_gate`; reference-rfc.md 'accept' steps 3-4 and 'Accepted is not terminal'; RFC0055-RFC0060 Accepted with open children; RFC0061 refused and forced (D0362).
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-09T15:11:40Z

## Summary

reference-rfc.md's accept step spawns the workstream CRs and then sets the RFC Accepted ('Accepted is not terminal. The RFC remains the living design home its CRs reference'), and RFC0055-RFC0060 were all Accepted at decision time with children open. transition.py's request-terminal gate (G2, transition.py:1060) treats an RFC's Accepted like a CR's Complete, derived from its children: `RFC0061 cannot be Accepted: its status is DERIVED from its children, and 4 is/are not yet resolved`. So the documented ceremony is refused at its last step, and the only route is `--force`, used for RFC0061 on 2026-10-09 (D0362).

## Steps to Reproduce

Resolve an RFC's decisions, spawn its CRs with `artifact.py new --type cr --parent RFCxxxx`, then `transition.py set --id RFCxxxx --status Accepted` -> refused while the CRs are Proposed.

## Proposed Fix

Decide which is right and make the other match: either an RFC's Accepted is the decision (exempt it from G2, and let a separate state mean 'delivered'), or reference-rfc.md's accept step stops setting Accepted and says the RFC moves when its CRs do.

## Acceptance Criteria

- [ ] **AC1** Following reference-rfc.md's accept steps through the shipped tools ends with the RFC in the state the reference names, with no --force
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_rfc_accept_with_open_children.py::RfcAcceptTests::test_the_documented_accept_needs_no_force

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Filed |
