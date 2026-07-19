# Audit Profile: repo

The packaged lens pack for the **zero-setup pass over an existing repository** - the
try-before-you-adopt entry point on code that has never run sdlc-studio. Three legs:
architecture, code quality, defensive security. Load this pack as the profile when
there is source to read and no artefact graph yet (vs the default project profile in
`reference-audit.md#audit-project-profile`).

> **Refute panel:** shared - 3 skeptics per candidate, survive on >= 2 of 3
> (`reference-audit.md#audit-refute`). This pack does not opt out.

Use each row as the `{{lens}}` / `{{lens_question}}` of `audit-finder.md`, one finder
per lens, looped until-dry; then the shared refute panel and filer.

| Lens | Adversarial question | Hunts for |
| --- | --- | --- |
| architecture | Where does the shape of this code fight the problem it solves? | boundaries that leak, a layer everything reaches through, cycles between modules, a seam that cannot be tested, state shared where ownership is unclear |
| code-quality | What here will be expensive to change, and why? | duplicated logic with drifting copies, functions doing several jobs, dead or unreachable code, error paths that swallow the cause, naming that misdescribes behaviour |
| defensive-security | How would an attacker or a mistake get through here? | unvalidated input reaching a sink, missing authentication or authorisation on a path that needs it, secrets in the tree, unsafe defaults, dependencies pinned to nothing |

## Security posture (binding)

Hand this wording to the defensive-security finder verbatim. It is the posture the
report is written to, not a suggestion:

Security findings are remediation-only by design: report location, weakness class,
realistic impact, and a concrete fix. Do not include proof-of-concept exploits or
payloads. Never copy a secret value into any artefact; report a committed secret by
its location plus rotation instructions, and leave the value where it is.

## Notes

- This pack is declarative: a lens is a name + an adversarial question + what it hunts.
  A project extends a profile by appending rows (see `reference-audit.md#audit-extend`).
- Read-only on source. Findings are filed as Bugs or CRs through `file_finding.py`, so
  ids and index rows are tool-allocated rather than hand-authored.
- On a repo with no workspace, the filer creates the folders and indexes it needs; the
  audit itself writes nothing else.
- Cheaper than the full project profile: three lenses, one round, no artefact graph to
  traverse. Estimate before launching (`audit_cost.py --lenses 3`).
