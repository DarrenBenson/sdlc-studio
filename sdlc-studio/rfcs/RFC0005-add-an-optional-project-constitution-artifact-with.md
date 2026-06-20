# RFC-0005: Add an optional project-constitution artifact with a machine-checkable principle gate

> **Status:** Draft
> **Priority:** Medium
> **Author:** Adversarial Audit
> **Date:** 2026-06-20
> **Spans:** sdlc-studio skill
> **Related:** RV0002 (audit run)
> **Supersedes / Superseded by:** --

## Summary

Project principles in SDLC Studio are unenforced prose (reference-doctrine.md plus agent-instructions); validate.py's instructions check only confirms an AGENTS.md exists. Spec Kit's constitution and Kiro's steering files make principles a re-applied, checkable gate; SDLC Studio has none, so architectural invariants can be silently ignored by generated artifacts.

## Context & Problem

grep for 'constitution' across the skill returns zero hits. reference-doctrine.md (105 lines) is the skill's own operating discipline (line 83: 'Don't stop mid-execution'), not project-specific inviolable constraints (e.g. 'all data access goes through the repository layer', 'no PII in logs'). The agent-instructions template is prose loaded when relevant. validate.py check_instructions (validate.py:156-174) only checks AGENTS.md presence/thinness, asserting no principle. No command injects principles into every artifact generation, and no constitution artifact exists whose principles validate.py check or review mechanically asserts against produced PRD/epic/story content. Spec Kit's /speckit.constitution establishes immutable principles its analyze step checks artifacts against; Kiro steering files are 'read on every interaction'.

## Design Options

### Option A - act on the finding

Add an optional project-constitution artifact (e.g. sdlc-studio/constitution.md) seeded at init, loaded as a generation constraint, with a validate.py / review check that flags artifacts violating explicitly-listed principles (e.g. 'every story must cite a parent epic', 'no AC without a Verify line'). RFC because it adds a new always-loaded-ish artifact type and a gating step, cutting against the lean-router goal and the broader push for fewer artifacts - so the trade needs an explicit call.

### Option B - status quo

Keep the current behaviour and accept the trade-off described above.

## Recommendation

TBD - pending the Open Decision below.

## Open Decisions

| # | Decision | Options | Owner | How it resolves | Status |
| --- | --- | --- | --- | --- | --- |
| D1 | Act on this finding or keep status quo | Option A / Option B | Operator | spike or operator call | Open |

## Evidence

grep -ril constitution across .claude/skills/sdlc-studio = 0 hits; scripts/validate.py:156-174 (check_instructions only verifies AGENTS.md presence/thinness); benchmark <https://github.com/github/spec-kit>

## Impact

Project-specific rules (security requirements, mandated patterns) are not enforced on generated artifacts; the model can silently ignore doctrine. Competitors make principles a re-applied constraint and a checkable gate, giving stronger guarantees than advisory prose. Quality risk medium.

## Decision

**Outcome:** TBD
**Rationale:** TBD

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Adversarial Audit | Filed from the 2026-06-20 audit (lens: external-benchmark) |
