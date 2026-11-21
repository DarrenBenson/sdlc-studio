# BG1569: The RFC accept workflow spawns CRs and then sets Accepted, which the transition gate refuses

> **Status:** Open
> **Supersedes:** BG1020
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/reference-rfc.md, .claude/skills/sdlc-studio/help/rfc.md, changelog.d/BG1569.md, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/reference-outputs.md, .claude/skills/sdlc-studio/reference-schema.md, .claude/skills/sdlc-studio/templates/core/rfc.md, .claude/skills/sdlc-studio/templates/indexes/rfc.md, .claude/skills/sdlc-studio/scripts/tests/test_status_vocab_doc.py
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

- [ ] **AC1** Given a fixture RFC whose every decision is resolved and one CR spawned from it at Proposed, when the accept steps reference-rfc.md documents are followed through `transition.py set` in the order written, then every step exits 0 without `--force` and the RFC holds the status the page names for a decided RFC. Fails on: the documented happy path refused, so that every accepted RFC is accepted by override.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RfcAcceptWorkflowTests::test_the_documented_accept_steps_pass_without_force
- [ ] **AC2** Given the same RFC with its spawned CR unresolved, when it is moved to the status that claims its workstreams are delivered, then the transition is refused naming the unresolved CR; once the CR is terminal the same transition succeeds. Fails on: the fix removing the derived gate instead of placing it at the status that claims delivery.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RfcAcceptWorkflowTests::test_the_delivery_claim_is_still_refused_over_an_unresolved_cr
- [ ] **AC3** Given reference-rfc.md and help/rfc.md, when the test reads the status each names for an RFC between decision and delivery and whether each calls Accepted terminal, then both agree with the RFC statuses and terminal set the tool holds, and an RFC with an Open decision row is still refused at the decided status. Fails on: the pages and the tool giving different accounts of what Accepted means, or the open-decision gate lost in the change.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RfcAcceptWorkflowTests::test_the_pages_and_the_tool_agree_on_what_accepted_means

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
| 2026-11-21 | Claude Opus 5.5 (run twenty-one orchestrator) | Affects widened in-run: D0513's Delivered status lives in the RFC vocabulary and terminal set (lib/sdlc_md.py) and the status tables and templates that state it; re-sized 3 to 5 for the vocabulary change |
