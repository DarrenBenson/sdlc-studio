# Help: gate

<!-- Load when: /sdlc-studio gate - running the ecosystem-neutral quality gate -->

## You can just ask

SDLC Studio is model-invoked - say it in plain language:

| Just say... | Runs |
| --- | --- |
| "Are we clear to commit this?" | `/sdlc-studio gate` |
| "Run the quality checks before I push" | `/sdlc-studio gate` |
| "Are we clear to tag?" | `/sdlc-studio gate --release` |
| "Can we close this sprint?" | `/sdlc-studio gate --require-retro RETRO0021` |
| "Is a sprint close still owed before I push?" | `/sdlc-studio gate --require-close` |
| "Just check the index and drift, nothing else" | `/sdlc-studio gate --only reconcile,duplicate-id` |
| "Skip the principles check this time" | `/sdlc-studio gate --skip constitution` |
| "Give me the gate result as JSON for the pipeline" | `/sdlc-studio gate --format json` |

A single, **ecosystem-neutral** quality gate over the deterministic checks. Run it in
any CI (or a pre-commit hook) to enforce the discipline on a consuming project's changes.

## Command

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/gate.py" --root .          # run all checks, exit 1 on a blocking failure
python3 "$CLAUDE_SKILL_DIR/scripts/gate.py" --root . --release  # pre-tag: the same gate + an executing AC verify pass
python3 "$CLAUDE_SKILL_DIR/scripts/gate.py" --only conformance,reconcile
python3 "$CLAUDE_SKILL_DIR/scripts/gate.py" --skip constitution --format json
```

Prints a consolidated report and exits non-zero only when a **blocking** check fails; a non-blocking
failure is reported (`warn`) but does not fail the gate. No network, no CI/cloud assumption.

## `--release`: the one command before a tag

The pre-tag ritual is otherwise two commands - the gate, plus a separate verify run whose exit
code you have to remember not to discard. `--release` makes it one:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/gate.py" --root . --release || exit 1   # do not tag on a red exit
```

It adds a blocking `verify` lane to the standard gate:

- **It executes.** Every story's `Verify:` expression is run *now*. It does not read the stored
  `verify-report.json`, because a merged report carries a story's last green forward until
  something re-runs it - and a stale green is exactly how a rotted verify layer reaches a tag.
- **It writes nothing.** No `- **Verified:**` back-annotation, no report rewrite. The gate stays
  read-only, so it is safe from a hook and safe to run twice.
- **It names the failures.** `2 red AC(s): US0001::AC3 (pytest tests/test_x.py::test_y), ...` -
  and the whole thing is one exit code, so tagging over a red AC layer means *ignoring a failing
  command* rather than misreading a passing-looking one.
- **You cannot deselect the lane and keep the verdict.** `--release --skip verify` (or an
  `--only` that leaves it out) is **refused**, not honoured: a release PASS printed over an
  unexamined AC layer is the passing-looking command this mode exists to abolish. Want the AC
  layer left alone? That is the standard gate - drop `--release`.

`--release` also binds a `review-legs` lane: every required **document leg** (PRD / TRD / TSD /
Persona) must be **present** or **explicitly waived**, or the release fails. A prose review can
call a missing leg "optional polish"; this lane cannot be talked around. Resolve an absent leg one
of two ways - add the artefact, or record a waiver:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/decisions.py" waive --leg tsd \
  --rationale "single-repo project; per-story Verify: discipline stands in for a TSD"
```

The lane then reports the leg as `waived (D00xx)`, never `optional`. The **CODE leg is out of
scope** (it has no single artefact whose presence can be tested); every verdict states that
exclusion, so a green lane is not misread as certifying the code. It is release-only for the same
reason as `verify`: a leg legitimately absent mid-build is not a standard-gate failure. Deselecting
it under `--release` is refused.

### Nothing to prove is not proof

The lane fails, rather than passing quietly, when it has examined nothing:

| Situation | Lane says |
| --- | --- |
| No stories under `sdlc-studio/stories` | FAIL - wrong `--root`, or a moved directory |
| A story with an **unspecified** AC (no `Verify:` line at all) | FAIL, and the story is named - so *deleting* a rotted `Verify:` line can never be the way to a green gate |
| A story whose ACs are all declared `Verify: manual` | PASS - a declared human-checked judgement is honest, and is not over-fired on |
| A verifier the trust boundary refused to run | FAIL, reported **BLOCKED**, never red (see below) |

The unspecified check is **per-story**, not repo-wide: an omitted `Verify:` line (nothing was
asserted about the AC) is distinct from a declared `Verify: manual` one (a judgement call). One
green executable AC elsewhere does not let a verifier-less story ride along - each story is judged on
its own ACs.

### The trust boundary (`--allow-external`)

A story stamped `Provenance: external` does not get to reach a shell: its `shell` / `http` / `eval`
verifiers are **not executed** (`reference-verify.md`). The lane reports those ACs as **unproven -
BLOCKED**, never as red, because an unrun verifier is not evidence about the code - calling it a
failing AC sends you to debug a verifier that works. Unproven still fails the gate. Pass
`--allow-external` to run them once you trust the content; the AC then goes green or red on its
own merits.

### Speed

`--verify-batch` runs jest **once** and resolves jest verifiers from the cached result, instead of
a cold start per AC. Worth it on any JS project with more than a handful of jest ACs - a slow
pre-tag command is one people route around.

A green `--release` is the *mechanical* half of the pre-tag checklist. The judgement items still
belong to the operator - see `templates/workflows/release-gate.md`.

## `--require-retro`: the one command that closes a sprint

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/gate.py" --root . --require-retro RETRO0021 || exit 1
```

The close's learning loop is one obligation, so one flag carries all of it. Three blocking lanes:

- `retro` - the named batch retro exists in `sdlc-studio/retros/`.
- `lessons-summary` - the committed `retros/LESSONS-SUMMARY.md` is the digest of the **current**
  lessons log. The lane recomputes that digest and compares, so a lesson **closed** since the last
  regeneration fails it just as an added one does; there is no freshness stamp to forge, and
  reformatting the file cannot false-fire it. Fix: `lessons summary`.
- `lessons-validity` - no open lesson is past its `Review-by` horizon, and none lacks one
  (unprovable is not proven). Fix: `lessons revalidate --close` / `--extend` / `--stamp`.

Summarising the sprint's lessons and reading them at the next sprint's start used to be prose,
and prose gets skipped under effort pressure. Now the close **fails loud** without it, and
`sprint plan` prints the lessons into the plan the next sprint reads. `--require-lessons` runs the
two lessons lanes alone (a close with no retro due). Deselecting a bound lane
(`--skip lessons-summary`) is refused, not honoured.

## `--require-close`: the guard against a silently-skipped close-down

The close-down (retro + lessons + close gate) is mandated, but `--require-retro` only fires when
someone remembers to run it. A ceremony with no detector is a **silent control** - it lapses under
delivery pressure, and the lessons quietly stop compounding. `--require-close` is the detector made
a gate:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/gate.py" --root . --require-close || exit 1   # before you push
```

It binds one blocking lane, `close-owed`: it **fails** when any delivery unit (epic / story / bug)
reached a terminal state since the close-owed baseline with no retro's `Batch` accounting for it.
A unit is **covered** the moment a retro names it. Put this on your push or release step; the plain
gate deliberately does **not** carry it, so a normal `gate` never claims to have checked
close-ownership.

The soft, discoverable half of the same signal is already on `status` and `hint` (an `advisory:`
line naming the owed units) - so a skipped close is seen where operators look, not discovered
sprints later.

**The baseline (run once, at adoption).** A project that adopts this after many sprints carries a
tail of historically-closed units that predate story-level retro batches. Stamp a one-time baseline -
the exact set of ids terminal at adoption - so only *later* closes can owe a retro:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/close_owed.py" baseline    # grandfathers the existing tail
python3 "$CLAUDE_SKILL_DIR/scripts/close_owed.py" detect      # what owes a close right now?
```

The pre-adoption tail is recorded and forgiven in `.close-owed-baseline.json`, never enforced
retroactively. Until a baseline is stamped the detector reports every uncovered unit and asks you to
baseline first, rather than inventing a cutoff.

**The Stop hook (optional).** `scripts/hooks/close_guard.py` wires the same detector into a project's
`.claude/settings.json` under `hooks.Stop`, so the agent is reminded of an owed close at the moment a
turn would end - the harness enforcing the Definition of Done's close clause rather than the agent's
recall. It is default-allow on any doubt and never hard-locks; a project that finds a per-turn
reminder too eager simply does not wire it and relies on `--require-close` at the push/release moment.
A sprint is complete only when the close gate is green and shown, **never at "deployed"**.

### The checks

| Group | Checks | Blocks? |
| --- | --- | --- |
| **Artifact quality** | `conformance` (lifecycle stages), `validate` (structure/vocab), `integrity` (required links/refs), `constitution` (project principles) | yes (constitution only when `constitution.enforce`) |
| **Engagement floor** | `engagement-floor` (a shipped multi-file unit with no AC / Verify / linked plan) | yes (advisory under `engagement_floor: judgement`) |
| **Index consistency** | `reconcile` (file-census drift), `duplicate-id` | yes |
| **Provenance** | `provenance` (tool-created stamps) | only when `provenance.enforce` |
| **Skill docs (skill repo only)** | `doc-coverage` (every command/script documented), `disclosure` (progressive-disclosure hygiene), `doc-freshness` (LATEST.md vs reality) | doc-coverage yes; disclosure + doc-freshness advisory |
| **Executable ACs (`--release` only)** | `verify` (executes every story's `Verify:` expression) | yes |
| **Required legs (`--release` only)** | `review-legs` (every required document leg present or waived; CODE out of scope) | yes |
| **Sprint close (`--require-retro` / `--require-lessons` only)** | `retro` (the batch retro exists), `lessons-summary` (LESSONS-SUMMARY.md is current), `lessons-validity` (no expired or horizon-less open lesson) | yes |
| **Close-owed guard (`--require-close` only)** | `close-owed` (no delivery unit reached terminal since the baseline with no covering retro) | yes |

The four **artifact-quality** checks are the ones that police every artifact; the rest guard the
index, provenance, and the skill's own docs. `--only` / `--skip` select a subset. The `verify`
lane only joins the registry under `--release` (it runs test suites; the standard gate stays fast
and read-only for a pre-commit hook).

## CI wiring (the gate is the mechanism; these are just examples)

### GitHub Actions

```yaml
- name: SDLC gate
  run: python3 .claude/skills/sdlc-studio/scripts/gate.py --root .
```

### GitLab CI

```yaml
sdlc-gate:
  script:
    - python3 .claude/skills/sdlc-studio/scripts/gate.py --root .
```

### Generic shell / pre-commit hook

```bash
# .git/hooks/pre-commit  (or any Jenkins/Buildkite/CircleCI step)
python3 .claude/skills/sdlc-studio/scripts/gate.py --root . || {
  echo "SDLC gate failed - fix drift/conformance before committing"; exit 1; }
```

Any runner that can execute a shell command can run the gate; nothing here is
GitHub-specific.

### Opt-in commit-msg gate (engagement floor)

A separate, opt-in `commit-msg` hook checks a commit subject that names more than
one work-item id (US/BG/CR) for a `Refs: <id>` trailer disambiguating them.
The trailer lets the engagement floor attribute a shared commit's files per id
(otherwise such a commit is skipped and an understated `Affects` goes uncaught).
Add `--strict` and it refuses the commit, printing the trailer lines to paste -
which is how this repo's own `.githooks/commit-msg` runs it, so the warning cannot
be read as enforcement while the commit lands anyway. Without `--strict` it warns
and exits 0. A single-id subject passes untouched either way. Wire it into any
project's own commit-msg hook:

```bash
# .git/hooks/commit-msg  ($1 is the message file git passes in)
python3 .claude/skills/sdlc-studio/scripts/engagement_floor.py check-commit-msg --strict "$1"
```

It degrades honestly: with no git, no script, or an unparseable message it exits
without blocking. See `reference-config.md` (Engagement Floor) for the trailer
grammar and the strict opt-in.

## See also

- `reference-scripts.md` - the script catalogue
- `reference-doctrine.md` - where the gate fits the operating discipline
