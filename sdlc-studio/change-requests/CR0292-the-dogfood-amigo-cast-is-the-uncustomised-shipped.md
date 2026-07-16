# CR-0292: The dogfood amigo cast is the uncustomised shipped default - grounded in a fictional shopping-list project and a nonexistent Primary - sitting in the retired personas/amigos/ home the repo's own migrator warns about

> **Status:** Complete
> **Decomposed-into:** EP0050
> **Priority:** Medium
> **Type:** process
> **Size:** S
> **Affects:** sdlc-studio/personas/amigos/product.md, sdlc-studio/personas/amigos/engineering.md, sdlc-studio/personas/amigos/qa.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

Two halves of one staleness. Content: the workspace's three amigo cards are byte-identical to the shipped template defaults except a provenance comment, despite each header saying 'Customise or replace per project' and the PRD claiming team generation from THIS project is Complete. Lena's scenario judges stories against 'the Primary persona, Sam the new shopper' - a persona that does not exist here (the Primary is Maya Okafor) and whose name collides with QA amigo Sam Eriksson; all three scenarios come from a to-do/shopping app, none from a CLI skill repo. Layout: the cast lives in personas/amigos/, the home the skill retired (RFC0021 convergence) - `persona_resolve.py` emits a live deprecation warning on every seat resolution ('personas/amigos/ is the retired home; migrate... to personas/seats/'), and `project_upgrade.py` --apply migrates mechanically, but the repo never ran its own migrator on itself. The seats that gate this repo's stories reason from a foreign project's ground truth through a warning path. Six panel votes, all not-refuted; CR0218/CR0219 built the tooling but no artefact covers pointing it at this workspace.

## Impact

Two halves of one staleness.

## Acceptance Criteria

- [x] The dogfood cast is migrated to personas/seats/ (`project_upgrade` --apply and/or persona generate --team), removing the retired amigos/ copies
- [x] Each seat card is grounded in this project: scenarios reference the skill repo's domain and its actual Primary (Maya); no 'Sam the new shopper' or shopping-app scenarios remain
- [x] `persona_resolve.py` resolves each seat without the retired-home warning

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Raised |
