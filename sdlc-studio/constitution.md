# SDLC Studio Constitution

The inviolable principles for this repository (RFC0005). Loaded as a generation
constraint; the machine-checkable principles are asserted by `constitution check`.
Advisory by default; `constitution.enforce: true` in `.config.yaml` makes a violation
fail the check.

## Principles

- **Every story traces to a parent epic.** `rule: story-requires-epic`
- **Every story declares acceptance criteria.** `rule: story-has-ac`
- **All cross-references resolve to a real artifact.** `rule: links-resolve`
- **Statuses come from the type's vocabulary.** `rule: status-in-vocab`
- **Indexes match the files on disk (no drift).** `rule: no-index-drift`
- **British English; no em dashes; no corporate jargon (robust/leverage/synergy).**
- **Paperwork ships in the same commit as the behaviour or doc change it records.**
- **Deterministic first: a new check, review or gate fires on a deterministic trigger (artifact fields, config, declared paths); model judgement acts inside a fired step, never in the fire/skip decision; skips are recorded operator overrides.**
  (TRD ADR-006; evidence D0014 - judgement-scaled hygiene was skipped 10/10 under pressure.)

## Checkable-rule vocabulary

See `templates/constitution.md` for the full rule vocabulary and how to declare
checkable vs advisory principles.
