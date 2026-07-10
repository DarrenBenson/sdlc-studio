# Skill Evals

Behavioural regression scenarios for the skill's *instructions* - the
counterpart to `scripts/tests/` (which covers the Python helpers) and
`tools/` (which covers structure). A description rewrite, a workflow
trim, or a re-routed reference can silently change what the model does;
these scenarios catch that before a release.

Run manually before tagging (release-gate section 1). Not CI: each run
costs a real model session.

## The two-Claude loop

Each scenario runs as **worker** then **grader**:

1. **Worker session.** A fresh agent session (no carried context) with
   the candidate skill installed. Set up the scenario's `setup` fixture,
   then send `prompt` verbatim. Save the full transcript.
2. **Grader session.** A second fresh session. Provide the transcript
   plus the scenario's `expected_behaviours` and `forbidden_behaviours`
   lists. Ask for a verdict per item: `pass` / `fail` / `unclear`, with
   one line of evidence each.
3. **Record.** Note results in the release-gate sign-off. Any failed
   `severity: blocking` behaviour blocks the tag; `advisory` failures
   need a triage note.

Grade against the transcript, not the artifacts alone - several
behaviours are about *how* the model got there (which files it read,
whether it paused).

## Scenario format

One JSON file per scenario in `scenarios/`:

| Field | Meaning |
| --- | --- |
| `id`, `title` | Stable identifier and human label |
| `regression_target` | What change class this scenario guards against |
| `setup` | Fixture to prepare before the prompt (paths, commands) |
| `prompt` | Sent to the worker verbatim |
| `expected_behaviours[]` | `{id, description, severity}` - graded individually |
| `forbidden_behaviours[]` | Things that fail the scenario if observed |
| `grading_notes` | Disambiguation for the grader |

## Current scenarios

| Scenario | Guards against |
| --- | --- |
| `01-trigger-routing` | Description rewrite breaking model invocation |
| `02-greenfield-create` | Create-path workflow regressions (epic/story trims) |
| `03-generate-mode-gate` | Philosophy gate skipped in brownfield generate mode |
| `04-drift-reconcile` | Script-backed status/reconcile flows and dry-run safety |
| `05-schema-v3-identity` | The v4 default: ULID id allocation, ULID-epic wiring, reconcile coverage |
| `06-independence-gate` | Author != reviewer and the verified-depth gate on terminal status |

Add a scenario whenever a release breaks behaviour these did not catch -
the gap is the spec for the next scenario.
