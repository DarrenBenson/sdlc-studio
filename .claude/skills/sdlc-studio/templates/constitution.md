# {{project}} Constitution

The project's inviolable principles. Optional. When present at
`sdlc-studio/constitution.md` it is loaded as a constraint during artifact generation,
and `constitution check` (RFC0005) asserts the machine-checkable principles across the
artifact graph.

A principle is **checkable** when it carries a `` `rule: <name>` `` from the vocabulary
below - the gate enforces it. A principle with no rule is **advisory**: it is listed and
loaded as a generation constraint, but not gated (structurally-uncheckable rules like
"no PII in logs" belong here).

Enforcement is advisory by default. Set `constitution.enforce: true` in
`sdlc-studio/.config.yaml` to make a violation fail `constitution check` (exit non-zero).

## Principles

- **Every story traces to a parent epic.** `rule: story-requires-epic`
- **Every story declares acceptance criteria.** `rule: story-has-ac`
- **Every acceptance criterion has an executable Verify line.** `rule: ac-requires-verify`
- **All cross-references resolve to a real artifact.** `rule: links-resolve`
- **Statuses come from the type's vocabulary.** `rule: status-in-vocab`
- **Indexes match the files on disk (no drift).** `rule: no-index-drift`
- **{{advisory principle, e.g. all data access goes through the repository layer}}**

## Checkable-rule vocabulary

| Rule | Asserts | Backed by |
| --- | --- | --- |
| `story-requires-epic` | every active story links a parent Epic | integrity |
| `story-has-ac` | every story has a populated Acceptance Criteria section | conformance |
| `ac-requires-verify` | every story carries a `Verify:` line | conformance |
| `links-resolve` | no dangling artifact reference | integrity |
| `status-in-vocab` | every Status is in the type vocabulary | validate |
| `no-index-drift` | every `_index.md` matches the files | reconcile |

> Delete the principles you do not want; add only those your project will hold. Keep the
> set small - a constitution is the handful of rules that must never be violated, not a
> style guide.
>
> **Note:** `story-has-ac` and `ac-requires-verify` honour `conformance.adopt_after` -
> stories below an adoption cutoff are exempt from these two rules (forward-only
> adoption), so they are not absolute once a cutoff is set.
