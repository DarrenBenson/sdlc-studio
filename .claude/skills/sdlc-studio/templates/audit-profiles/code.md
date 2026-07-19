# Audit Profile: code

The packaged lens pack for auditing an **implementation** rather than the
specification set around it. Use it when the artefact graph is sound and the
question is whether the code under it does what it claims (vs the default project
profile in `reference-audit.md#audit-project-profile`, which hunts across artefacts).

> **Refute panel:** shared - 3 skeptics per candidate, survive on >= 2 of 3
> (`reference-audit.md#audit-refute`). This pack does not opt out.

Use each row as the `{{lens}}` / `{{lens_question}}` of `audit-finder.md`, one finder
per lens, looped until-dry; then the shared refute panel and filer.

| Lens | Adversarial question | Hunts for |
| --- | --- | --- |
| correctness | Which input makes this behave differently from what it promises? | off-by-one and boundary cases, wrong operator precedence, an empty or absent value treated as a wildcard, concurrency assumed away, a caught exception that hides the fault |
| security-smells | What here trusts something it should check? | input flowing to a sink unvalidated, authorisation checked in one path and not its sibling, a secret in the tree, a comparison on secrets that is not constant-time, defaults that open rather than close |
| pattern-violations | Where does this contradict the practice the project has already chosen? | a duplicated helper the shared library already provides, a layering rule broken once, an error convention used inconsistently, a config key read directly around its accessor |
| ac-drift | Where does the code diverge from the acceptance criterion it was built for? | an AC satisfied only on the happy path, a test asserting what the code does rather than what the AC says, a criterion marked met by a check that cannot fail, behaviour shipped that no AC asked for |

## Notes

- This pack is declarative: a lens is a name + an adversarial question + what it hunts.
  A project extends a profile by appending rows (see `reference-audit.md#audit-extend`).
- `ac-drift` needs the unit's ACs in the finder's context. Give the finder the story or
  bug alongside the diff scope, or it degrades into a second correctness pass.
- Security findings follow the same remediation-only posture the repo pack states
  (`audit-profiles/repo.md`): location, weakness class, impact and fix, never a payload
  and never a copied secret value.
- Read-only on source; survivors are filed through `file_finding.py`.
