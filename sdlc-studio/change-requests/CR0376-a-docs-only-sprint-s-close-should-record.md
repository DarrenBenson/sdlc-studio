# CR-0376: a docs-only sprint's close should record the mutation step as an explicit skip, not an error to work around

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/gate.py
> **Date:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The close's mutation evidence step runs mutation.py over the sprint diff; a diff with no mutatable files (docs, templates, artefacts) exits 2 with 'no mutatable files in the selected surface', so a docs-only close either fails a step or the operator skips it silently - and a silent skip reads identically to forgotten evidence. The gate's mutation lane should be able to say 'nothing to mutate this sprint' as a first-class, recorded outcome, exactly as the pre-commit hook already names its docs-only unit-suite skip. Cost data from RUN-01KXZQF0 (RETRO0060): evidence runs cost ~40min wall on a code sprint, so exempting docs-only sprints is the cheapest lever there is.

## Impact

every docs-only or artefact-only sprint close; today each one ends in a worked-around error that is indistinguishable from missing evidence

## Acceptance Criteria

- [ ] mutation.py run over a surface with no mutatable files can emit a report recording the empty surface as the honest outcome (exit 0 under an explicit flag or a distinct recorded status), never a silent pass
- [ ] the gate's mutation lane reads that report as 'nothing to mutate' - distinct from not-run and from PASS - so a docs-only close is green with the reason on the record

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Raised |
