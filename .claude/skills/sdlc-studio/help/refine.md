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

## What it refuses, and why

| Refusal | Reason |
| --- | --- |
| a story whose `Affects` resolves to nothing | a unit `sprint plan` would refuse as ungroomed - caught here, before an id is spent |
| a request with no `Status` line | its `Decomposed-into:` link cannot be wired |
| points off the Fibonacci scale | the estimate stops being comparable with every other unit |

An `Affects` naming only files the unit will CREATE is refused when NONE of them resolves.
Anchor it to one existing path the work touches.

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
