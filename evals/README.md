# Skill Evals

Behavioural regression scenarios for the skill's *instructions* - the
counterpart to `scripts/tests/` (which covers the Python helpers) and
`tools/` (which covers structure). A description rewrite, a workflow
trim, or a re-routed reference can silently change what the model does;
these scenarios catch that before a release.

Run manually before tagging (release-gate section 1, and section 8 for a
major). Not CI: each scenario costs two real model sessions.

## The two-Claude loop

The mechanical ceremony is scripted: `python3 tools/eval_run.py setup --scenario <id>
--dir <scratch>` builds the fixture from the scenario's machine-readable `fixture`
spec and prints the worker prompt and the behaviours to grade; `record` logs each
graded behaviour; `report` is the gate. Every scenario carries a `fixture`; one
without it degrades honestly (setup prints the prose and exits 1). The worker and
grader sessions remain irreducibly judgement.

Each scenario runs as **setup**, **worker**, **grader**, **record**:

1. **Setup.** Build the fixture into a fresh scratch directory, then commit
   it as the base (`git init`, `git add -A`, `git commit`), so a behaviour
   such as "the dry run wrote nothing" can be proved with `git status`.
2. **Worker session.** A fresh agent session (no carried context) started
   in the fixture directory with the candidate skill installed. Send the
   printed prompt verbatim. Save the full transcript. Run it with the
   command `setup` prints, `CLAUDE_CONFIG_DIR=<dir>.claude-config claude -p ...`:
   under `claude -p` a personal `~/.claude/skills/sdlc-studio` is not
   outranked by a project copy, so without it the worker can load your
   installed skill instead of the candidate. `setup` copies this working
   tree's skill into that directory and never a credential: copy
   `~/.claude/.credentials.json` in yourself (mode 600) and delete it after
   the run.
3. **Grader session.** A second fresh session. Give it the transcript,
   the fixture directory and the behaviours `setup` printed. It grades
   every expected behaviour (`EB1`...) `pass` or `fail`, and every
   forbidden behaviour (`FB1`..., positional) `fail` if observed, else
   `pass`, with one line of evidence each.
4. **Record.** From the repository root, once per graded behaviour:
   `python3 tools/eval_run.py record --run <label> --scenario <id>
   --behaviour <EBn|FBn> --verdict <pass|fail> --evidence "<one line>"`.
   Then `python3 tools/eval_run.py report --run <label>` is the gate: it
   enumerates every scenario on disk, so a scenario nobody graded fails
   it; a failed blocking behaviour or an observed forbidden one blocks
   the tag; an advisory failure needs a triage note. For a run that
   re-measures only some scenarios (one re-run against a fix), `report
   --run <label> --scenario <id>` judges that scenario alone. The run file
   (`evals/.results/<label>.json`, committed with `git add -f`) and the
   release notes carry the result.

Grade against the transcript, not the artifacts alone - several
behaviours are about *how* the model got there (which files it read,
whether it paused).

## Scenario format

One JSON file per scenario in `scenarios/`:

| Field | Meaning |
| --- | --- |
| `id`, `title` | Stable identifier and human label |
| `regression_target` | What change class this scenario guards against |
| `setup` | The fixture in prose, for the reader |
| `fixture` | `{"files": {relpath: content}}` - what `setup` writes |
| `prompt` | Sent to the worker verbatim |
| `expected_behaviours[]` | `{id, description, severity}` - graded individually |
| `forbidden_behaviours[]` | Things that fail the scenario if observed; recorded as `FB1`..., always blocking |
| `grading_notes` | Disambiguation for the grader |

## Current scenarios

| Scenario | Guards against |
| --- | --- |
| `01-trigger-routing` | Description rewrite breaking model invocation |
| `02-greenfield-create` | Create-path workflow regressions (epic/story trims) |
| `03-generate-mode-gate` | Philosophy gate skipped in brownfield generate mode |
| `04-drift-reconcile` | Script-backed status/reconcile flows and dry-run safety |
| `05-schema-v3-identity` | The schema v3 default: ULID id allocation, ULID-epic wiring, reconcile coverage |
| `06-independence-gate` | A self-review counting as review; a bug reaching Fixed without green criteria and one independent APPROVE, or stalled on a depth tier nothing asks for |
| `07-team-generation` | Ask-before-write on ambiguous signals; never-clobber; the seats floor |
| `08-consult-objection-quota` | Anti-sycophancy: >=1 objection per seat; the Primary test arbitrates a buyer-serving feature |
| `09-lean-sprint` | A lean sprint the shipped docs cannot carry from plan to close: a skipped or self-run review, a hand-rolled step, or a worker that signs its own run |

Add a scenario whenever a release breaks behaviour these did not catch -
the gap is the spec for the next scenario.
