<!--
Load when: /sdlc-studio issue or /sdlc-studio issue help
Dependencies: SKILL.md (always loaded first)
Related: help/triage.md (the ceremony that decomposes an Issue), help/bug.md
-->

# /sdlc-studio issue - Issues (the defect-side Discovery item)

An **Issue** is a raw defect report: a symptom someone observed, not yet reproduced or scoped. It
sits in the **Discovery backlog** alongside RFCs and CRs - a thing to look into, not committed
work. You turn it into deliverable work by **triaging** it into concrete, reproducible **bugs**
(see `help/triage.md`). This mirrors the request side, where a CR/RFC is **refined** into stories.

Why a separate type, when a bug already exists? Because in real life you triage first: a report
arrives ("checkout sometimes 500s"), and only after investigation does it become one or more bugs
(or turn out to be a change, in which case you file a CR). The Issue is the intake term; the bug
stays the concrete delivery unit it already is.

## You can just ask

| Just say... | Runs |
| --- | --- |
| "Log an issue: checkout 500s intermittently" | `/sdlc-studio issue create` |
| "Show the open issues" | `/sdlc-studio status backlog` |
| "Triage issue IS0001 into bugs" | `/sdlc-studio triage apply --issue IS0001 ...` |

## File an Issue non-interactively (the canonical path)

```bash
python3 <skill>/scripts/artifact.py new --type issue \
  --title "Checkout 500s intermittently" \
  --severity High --size M \
  --summary "Sporadic 500 at checkout, no clear trigger yet"
```

An Issue carries:

- a **Severity** (Critical/High/Medium/Low) - the urgency a triager prioritises on;
- a T-shirt **Size** (S/M/L/XL) - the coarse Discovery estimate, exactly as a CR/RFC carries one;
- **no story points** - it is not a delivery unit. Points live on the bugs it produces.

Ids and index rows are **tool-allocated** - never hand-author `IS0001-...md` or the `_index.md`.

## Lifecycle

```text
   Open ─[triage]→ Triaging → Triaged ─[bugs all resolved]→ Resolved
     │                                                          (DERIVED, not asserted)
     └─[not a real defect]────────────────────────────→ Won't Fix / Closed / Superseded
```

- **Open** - raw intake; not yet accepted. A reconcile does NOT flag an Open Issue.
- **Triaging** - being worked. An accepted Issue with no bugs yet is flagged `undecomposed`
  (needs triage) by `reconcile detect` when the two-backlog workflow is enforced.
- **Triaged** - decomposed into bugs (written by `triage apply`), now delivered via them.
- **Resolved** - the successful terminal, reached only by DERIVATION when every bug it produced is
  resolved. `transition` refuses to assert it while a child is unresolved (G2).
- **Won't Fix / Closed / Superseded** - abandonment terminals; an Issue that is not a real defect,
  a duplicate, or superseded. These close WITHOUT children, because they assert no delivery.

## When it is really a change, not a defect

If triage reveals the report is a feature/behaviour change rather than a bug, do NOT force it into
a bug. File a **CR** and `refine` that instead - the request path. `triage` surfaces this option
and keeps the defect path clean.

## Gates (when `two_backlog.enforce` is on)

- `sprint plan` **refuses** an Issue - it is Discovery, with no executable ACs to close on.
- `status backlog` buckets it under **Discovery**, never Delivery.
- `reconcile detect` flags an accepted (Triaging) but childless Issue as `undecomposed`.
- `transition` derives the Issue's Resolved from its bugs (G2).

## See Also

- `help/triage.md` - the ceremony that decomposes an Issue into bugs
- `help/bug.md` - the delivery unit an Issue produces
- `reference-scripts-create.md` - `triage.py` internals
