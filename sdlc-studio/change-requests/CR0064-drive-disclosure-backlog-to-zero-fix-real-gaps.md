# CR-0064: drive disclosure backlog to zero fix real gaps and refine the check

> **Status:** Complete
> **Created:** 2026-06-21
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Improvement

## Summary

The disclosure check (CR0063) reported 66 advisories - all in the skill's own source. Triage:
28 real gaps + 38 false-positives where the check was too strict. Fix the real ones AND refine
the check so it reports 0 honestly (no future noise). All in this repo; none in consuming projects.

## Acceptance Criteria

- [x] refine `disclosure.py`: help/<type>.md reachable via the `help/{type}.md` pattern (not literal
  names); template placeholder check scoped to `templates/core/` (fill scaffolds), not modules/prompts
- [x] `chmod +x` the 24 CLI scripts (shebang + argparse); 4 `Load when:` markers added; the 2
  reference-sections files indexed in help/references.md
- [x] `disclosure --root .` reports 0; a real orphan / core-template-without-placeholder still flags
  (no regression); gate green
- [x] tests cover the refinements + the no-regression cases

## Implementation

Two `disclosure.py` refinements (help-pattern reachability; template check scoped to core) cleared
the 38 false-positives; chmod +x on the 24 scripts, 4 markers (reference-rfc, help/gate, help/pvd,
help/skill-update), and indexing the two section files cleared the 28 real gaps. disclosure now 0.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Autosprint | Created via `new` (deterministic) |
