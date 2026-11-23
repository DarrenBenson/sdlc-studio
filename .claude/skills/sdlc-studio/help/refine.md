<!--
Load when: /sdlc-studio refine or /sdlc-studio refine help
Dependencies: SKILL.md (always loaded first)
Related: help/triage.md (the defect-side mirror), reference-verify.md (writing a Verify line)
-->

# /sdlc-studio refine - decompose a request into an epic and its stories

`refine` turns a **CR or RFC** into the **epic and stories** that deliver it, wiring the
`Parent:` / `Decomposed-into:` links the two-backlog gates verify. A request sits in the
Discovery backlog; it becomes DELIVERY work only by being broken down into sized units, and
this is that step made a command rather than something an operator does by hand.

It is the mirror of `triage`, which turns an Issue into bugs. Where `triage` builds one level -
a bug is already the delivery unit - `refine` builds two.

## Show, then apply

```bash
# is this request refinable, and what does it already carry?
python3 <skill>/scripts/refine.py show --request CR0001

# decompose it (validated WHOLE before anything is minted)
python3 <skill>/scripts/refine.py apply --request CR0001 --breakdown breakdown.json

# a second epic against an already-decomposed request
python3 <skill>/scripts/refine.py add --request CR0001 --breakdown more.json
```

A breakdown document, which is the recommended path - prose never crosses a shell:

```json
{
  "epic-title": "What this slice of the request delivers",
  "stories": [
    {"title": "One deliverable behaviour", "points": 5, "affects": "src/a.py, tests/test_a.py"},
    {"title": "Another", "points": 3, "affects": "inherit"}
  ]
}
```

`--dry-run` validates and mints nothing. Use it first: `refine` checks the whole breakdown
before allocating an id, so a bad point value or an unresolvable `Affects` refuses cleanly and
leaves no half-decomposition behind.

## Refining part of a request

A request can be refined one slice at a time. Name the criteria a refine leaves undecomposed
with `--unrefined`, by label: `AC3` is the request's third acceptance criterion.

```bash
# this slice delivers AC1 and AC2; AC3 and AC4 are left for later
python3 <skill>/scripts/refine.py apply --request CR0001 --breakdown breakdown.json --unrefined AC3,AC4

# the next slice delivers AC3; AC4 is still left
python3 <skill>/scripts/refine.py add --request CR0001 --breakdown more.json --unrefined AC4

# the last slice: nothing is left
python3 <skill>/scripts/refine.py add --request CR0001 --breakdown last.json --unrefined none
```

The labels are written to the request's `> **Unrefined:**` field, and the criteria they name
are not seeded into the stories or the epic the refine mints. On `add`, `--unrefined` replaces
the record with what is still left after that slice; an `add` without it leaves the record as
it stands. A label the request does not carry, or a value that is not a label, is refused
before an id is minted.

Where the project enforces the two-backlog workflow (`two_backlog.enforce`), a request whose
record names a criterion is not complete, even when every child it produced is resolved:
`reconcile` names the criteria left and does not derive the request, and `transition.py set`
refuses its successful terminal unless forced. If the criteria left are dropped rather than
built, clear the record with `transition.py annotate --id CR0001 --field Unrefined --value none`.

## What it refuses, and why

| Refusal | Reason |
| --- | --- |
| a story whose `Affects` resolves to nothing | a unit `sprint plan` would refuse as ungroomed - caught here, before an id is spent |
| a request with no `Status` line | its `Decomposed-into:` link cannot be wired |
| points off the Fibonacci scale | the estimate stops being comparable with every other unit |

An `Affects` naming only files the unit will CREATE is refused when NONE of them resolves.
Anchor it to one existing path the work touches.

## The risk class each story carries

When the project declares a component map (`risk.components` in `sdlc-studio/.config.yaml`),
each story `apply` or `add` mints carries `> **Risk-class:**`: the highest of `standard`,
`elevated` or `high` among the components its `Affects` touch, inherited or seeded `Affects`
included. A path no component covers is `standard`. Nothing here refuses: with no map every
story is `standard` and one line says so, and an entry naming an unknown class is reported in
one line and read as `standard`. See
[reference-config.md#risk-map](../reference-config.md#risk-map).

## The grooming cost, stated plainly

A refined story arrives **ungroomed**: its acceptance criteria are a marker, not content. That
marker names where to go next - `templates/core/story.md` for the shape, `reference-verify.md`
for writing a `Verify:` line that actually runs.

Authoring those criteria is real work and it is **not** priced by the story's points, which
size the delivery the story describes. Budget it separately, or run `--goal design` first.
A batch of freshly refined stories is not a plannable batch until they are groomed - and
`sprint plan` will say so.

## Related

- [help/triage.md](triage.md) - the defect-side mirror
- [reference-verify.md](../reference-verify.md) - what makes a `Verify:` line executable
- [reference-sprint-toolchain.md](../reference-sprint-toolchain.md) - which command performs each step
