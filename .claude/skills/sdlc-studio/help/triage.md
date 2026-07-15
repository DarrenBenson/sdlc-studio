<!--
Load when: /sdlc-studio triage or /sdlc-studio triage help
Dependencies: SKILL.md (always loaded first)
Related: help/issue.md (the type it decomposes), reference-scripts-create.md (triage.py)
-->

# /sdlc-studio triage - decompose an Issue into bugs

`triage` is the defect-side decomposition ceremony: it turns an **Issue** (a raw Discovery report)
into the concrete, reproducible **bugs** that deliver its fix, wiring the two-backlog links so the
gates can verify the chain. It is the mirror of `refine` (which turns a request into an epic +
stories). Where `refine` builds two levels, `triage` builds one: a bug is already the delivery
unit, so no container is minted - the bugs hang directly off the Issue.

This is where a human clarifies the report: is it reproducible? one defect or several? really a
change rather than a bug? A team member can triage the Discovery backlog ahead while another
delivers the current sprint - the two-backlog gates are what make that safe to run in parallel.

## Show, then apply

```bash
# inspect the Issue and confirm it is triageable
python3 <skill>/scripts/triage.py show --issue IS0001

# decompose it into bugs (each: title|points[|severity[|affects]])
python3 <skill>/scripts/triage.py apply --issue IS0001 \
  --bug "Null cart total throws at checkout|3|High|src/checkout.py" \
  --bug "Retry storm on gateway timeout|5|Medium|src/gateway.py" \
  --question "Same root cause in both reports?"
```

`apply` validates the WHOLE breakdown before minting anything:

- the Issue must resolve, be an Issue, and not already be triaged;
- every bug's points must be on the Fibonacci scale (1, 2, 3, 5, 8, 13, 20);
- every bug is dry-run through the grooming gate first (a resolvable `Affects`, a size), so a bad
  bug fails **loud and empty** - it never leaves an earlier bug half-minted.

Then it creates each bug (`Parent:` the Issue), writes the Issue's `Decomposed-into:`, and moves
the Issue to **Triaged**. The Issue reaches **Resolved** only by derivation, when its bugs are all
resolved.

`--question` items are directed at the **Three-Amigos consult**, QA-led (QA leads a triage: is it
reproducible? what is the real defect?). The panel resolves to the actual named seats - the project's
own, or the shipped defaults (Sam Eriksson qa, Dani Okafor engineering, Lena Marsh product) - and the
consult is recorded on the Issue (a `> **Consulted:**` line + an `## Amigo Consult` section) so the
audit trail shows who was asked and what. `--skip-personas` forces the generic path (no seats, no
framing). Resolve the panel yourself with `persona_resolve.py panel --ceremony triage`.

## Refusals

| Situation | What triage does |
| --- | --- |
| The id is a CR/RFC, not an Issue | Refused - a request is **refined**, not triaged (use `refine.py`) |
| The Issue is already triaged | Refused - it already has its bugs |
| No `--bug` given | Refused - an empty triage delivers nothing; close it Won't Fix instead |
| A bug's `Affects` does not resolve | Refused up front - nothing minted |
| The report is really a change | Not triaged into a story here - file a CR and `refine` that |

## Why bugs, not stories

An Issue triaged into a **story** would need an epic parent (a story cannot hang off an Issue), and
a story implies a change rather than a defect. So `triage` produces **bugs** - the clean defect
path. When the report is genuinely a change, the honest move is a CR through `refine`, not a story
smuggled in via triage.

## See Also

- `help/issue.md` - the Issue type this decomposes
- `help/bug.md` - the delivery unit triage produces
- `reference-scripts-create.md` - `triage.py` and `refine.py` internals (shared link writers)
