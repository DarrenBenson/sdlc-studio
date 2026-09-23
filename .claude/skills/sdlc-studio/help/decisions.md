# `/sdlc-studio decisions`

The project decisions log, `sdlc-studio/decisions.md`: the append-only record of load-bearing
decisions every later artefact and delegated agent inherits. Driven by `scripts/decisions.py`.

## Commands

| Command | Does |
| --- | --- |
| `decisions.py add --decision D --rationale R` | Append a decision (auto-numbered `D{NNNN}`, dated) |
| `decisions.py list [--status S]` | Print the log, optionally filtered by status |
| `decisions.py promote --from PRD-OQ3 ...` | Record a resolved PRD open question with a back-link |
| `decisions.py waive --leg L \| --subject S` | Record a waiver: a leg or rule is out of scope here |
| `decisions.py rule --seat S --subject K ...` | A persona seat's binding ruling on a question |
| `decisions.py precedent --subject K [--question Q]` | The prior rulings a seat must cite or depart from |

## Persona rulings

A question the run raises goes to a persona seat (`engineering`, `qa`, `product`) before it
goes to the operator. The seat answers with `rule`, and the answer binds later runs:

```bash
python3 scripts/decisions.py precedent --subject deps:action-pins --question "may a workflow use a tag?"
python3 scripts/decisions.py rule --seat engineering --subject deps:action-pins \
  --question "may a workflow use a tag?" --ruling "no, pin a commit sha" \
  --reason "a tag can move under us"
```

- **Subject** is a short key, normalised like a waiver subject (`Deps:Action-Pins` and
  `deps:action-pins` are one key). The row reads `ruling: <subject> [seat: <seat>] <question>
  -> <ruling>`, so the log keeps its six columns.
- **Precedent** lists at most 3 accepted, non-superseded rows: rulings on the same subject
  first (newest first), then rows anywhere in the log that share the question's keywords,
  including rows written before subjects existed.
- **A subject already ruled on is refused** unless the seat either follows one of its
  rulings with `--cites Dxxxx` (nothing new is written; the cited ruling is printed; citing any
  other decision is refused and the subject's rulings are named) or departs from it with
  `--differs REASON` (a new ruling whose rationale names the subject ruling it departs from).
  A subject with no ruling yet may cite any live decision, and `--differs` there names nothing.
- **An open run counts who answered.** Each `rule` (including a citation) adds a `persona`
  entry to the run state's `rulings` list. `add`, `promote` and `waive` add an entry only with
  `--by operator` (the operator was asked) or `--by persona`; without `--by` the row is
  recorded but counted as neither, so an agent's own `add` never inflates the operator count.
  Between runs nothing is counted.

`--fields-file FIELDS.json` (or `-` for stdin) supplies the prose fields as JSON instead of
flags, so text carrying shell metacharacters is stored verbatim. Every verb takes
`--format json`.
