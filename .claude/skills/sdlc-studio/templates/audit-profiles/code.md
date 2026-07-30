# Audit Profile: code

The packaged lens pack for auditing an **implementation** rather than the
specification set around it. Use it when the artefact graph is sound and the
question is whether the code under it does what it claims (vs the default project
profile in `reference-audit.md#audit-project-profile`, which hunts across artefacts).

> **Refute panel:** shared - 3 skeptics per candidate, survive on >= 2 of 3
> (`reference-audit.md#audit-refute`). This pack does not opt out.

Use each row as the `{{lens}}` / `{{lens_question}}` of `audit-finder.md`, one finder
per lens, looped until-dry; then the shared refute panel and filer.

| Lens | Adversarial question | Hunts for | Signature |
| --- | --- | --- | --- |
| correctness | Which input makes this behave differently from what it promises? | off-by-one and boundary cases, wrong operator precedence, an empty or absent value treated as a wildcard, concurrency assumed away, a caught exception that hides the fault | manual - a wrong bound is intent measured against behaviour, and nothing in the tree distinguishes a deliberate inclusive bound from a mistaken one |
| security-smells | What here trusts something it should check? | input flowing to a sink unvalidated, authorisation checked in one path and not its sibling, a secret in the tree, a comparison on secrets that is not constant-time, defaults that open rather than close | rg -ni "(secret\|password\|passwd\|api.?key\|token)\w*\s*=\s*[\"']" . |
| pattern-violations | Where does this contradict the practice the project has already chosen? | a duplicated helper the shared library already provides, a layering rule broken once, an error convention used inconsistently, a config key read directly around its accessor | manual - the chosen practice lives in `best-practices/` as prose, and whether a helper duplicates one the shared library already provides is a judgement no search settles |
| ac-drift | Where does the code diverge from the acceptance criterion it was built for? | an AC satisfied only on the happy path, a test asserting what the code does rather than what the AC says, a criterion marked met by a check that cannot fail, behaviour shipped that no AC asked for | python3 .claude/skills/sdlc-studio/scripts/verify_ac.py lint |

## Notes

- This pack is declarative: a lens is a name + an adversarial question + what it hunts.
  A project extends a profile by appending rows (see `reference-audit.md#audit-extend`).
- `ac-drift` needs the unit's ACs in the finder's context. Give the finder the story or
  bug alongside the diff scope, or it degrades into a second correctness pass.
- Security findings follow the same remediation-only posture the repo pack states
  (`audit-profiles/repo.md`): location, weakness class, impact and fix, never a payload
  and never a copied secret value.
- Read-only on source; survivors are filed through `file_finding.py`.
