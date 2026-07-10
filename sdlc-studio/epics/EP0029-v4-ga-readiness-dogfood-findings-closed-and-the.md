# EP0029: v4 GA readiness: dogfood findings closed and the big-bang documented

> **Status:** Done
> **Created:** 2026-07-10
> **Created-by:** sdlc-studio new

## Summary

The final pre-GA sprint: close the findings raised while dogfooding the v4 line end-to-end
(the reconcile breakdown blind spot, the untooled eval gate, the three-verb bug close, the
missing local-source install), make the v2->v3 numbering switch an explicit operator
question in the upgrade flow, and finish with one coherent big-bang v4 documentation pass
so a newcomer reads v4 as the product. Docs land last (wave 2) so they document the
delivered behaviour, not the plan.

## Story Breakdown

- [x] [BG0101](../bugs/BG0101-reconcile-is-blind-to-epic-story-breakdown-checkbox.md) - reconcile blind to epic breakdown checkbox drift for bug/CR units
- [x] [CR0216](../change-requests/CR0216-project-upgrade-must-explicitly-ask-the-operator-before.md) - project upgrade explicitly asks before switching id numbering
- [x] [CR0212](../change-requests/CR0212-eval-run-a-deterministic-runner-for-the-two.md) - eval run: deterministic runner for the two-Claude eval gate
- [x] [CR0214](../change-requests/CR0214-install-sh-local-source-mode-install-the-working.md) - install.sh local-source mode (install the working tree)
- [x] [CR0213](../change-requests/CR0213-one-call-gated-terminal-transition-for-bugs-depth.md) - one-call gated terminal transition for bugs
- [x] [BG0102](../bugs/BG0102-project-upgrade-apply-stamps-schema-version-back-to.md) - upgrade --apply stamps schema_version back to 2 on a v3 project (found mid-sprint)
- [x] [CR0217](../change-requests/CR0217-living-personas-are-the-explicit-default-for-reviews.md) - living personas the explicit default for reviews/critics/consults (operator, mid-sprint)
- [x] [CR0215](../change-requests/CR0215-big-bang-v4-documentation-pass-every-consuming-facing.md) - big-bang v4 documentation pass (wave 2: after every behaviour above)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | sdlc | Created via `new` (deterministic) |
