# CR-0257: Sprint sizing ignores the captured Effort estimate, and bugs carry no size at all

> **Status:** Proposed
> **Priority:** P3
> **Type:** Improvement
> **Date:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/templates/core/bug.md, .claude/skills/sdlc-studio/scripts/file_finding.py

## Summary

Two disconnected size vocabularies. CRs carry a human Effort: S/M/L field captured at filing, but sprint.py never reads it - its WSJF size comes only from a seat-scored estimate (.local/wsjf-inputs.json) or the cognitive complexity of a unit's Affects files, falling back to `DEFAULT_UNKNOWN_SIZE`=3. So for a backlog with no Affects declarations and no seat-scoring (the common case), WSJF collapses to plain priority order and the token forecast collapses to a flat `BASE_TOKEN_BUDGET` x `unit_count` (proven: the internal-hardening plan forecast ~500k = 50k x 10, complexity contributing zero). The one estimate a human actually recorded does not count. Bugs are worse off: they have no effort/size field at all, only Severity (which is priority, not size), so a bug can never be sized even in principle.

## Impact

Every sprint plan whose units lack Affects declarations or seat-scoring - i.e. most of them. The token forecast and WSJF ordering are currently uninformed (flat per-unit constant), so 'sizing' gives the operator no real signal despite an Effort estimate being on file. Fixing it makes the estimate the operator already provides actually shape the plan.

**Effort:** M

## Acceptance Criteria

- [ ] sprint.py reads the CR Effort field and uses it as a WSJF size input when no seat-score is present, ranked above the unknown default. Verify: rg -q -i 'effort' .claude/skills/sdlc-studio/scripts/sprint.py
- [ ] Bugs carry an effort field (template + filer), so a bug can be sized. Verify: rg -qi 'effort' .claude/skills/sdlc-studio/templates/core/bug.md
- [ ] The token forecast reflects Effort when Affects/complexity is absent, rather than a flat base x count. Verify: python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -k sprint

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Raised |
