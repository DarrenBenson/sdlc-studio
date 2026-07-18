# SDLC Studio Reference - Executable Acceptance Criteria

<!-- Load when: authoring/running AC `Verify:` lines, `reconcile --verify`, or test-specs -->

> **The complement - can the test fail?** `verify_ac` proves an AC's tests PASS; the
> mutation-check gate (`scripts/mutation.py`, `help/mutation.md`) proves they would FAIL
> if the feature broke, by fault-injecting the changed surface and reporting killed vs
> survived. A green verify plus a survivor-free mutation report is the full
> assertion-integrity claim.
>
> **Human-checked ACs:** author the Verify line as `Verify: manual <what to check>`. A line led
> by `manual` (or `manually`) is counted **manual** - never executed - so a prose check can't be
> shelled out and time out into a false `failed`.
>
> **The test-spec is the AC-to-test bridge.** When an epic is fanned out, the AC's
> test name and the implementation's test title are chosen by different processes and drift
> into two parallel descriptions (the 0/7 class). Authoring the test-spec's **AC Coverage
> Matrix** *before* code fixes the test-case names that the Verify line and the test both
> adopt - convergence by construction. So at **epic-implement / sprint scope** author a
> test-spec (optional for a single story); keep the matrix honest with
> `verify_ac ts-check --spec <ts> [--verify-report <json>]` (every AC mapped to a passing
> test case, cross-checked against the live report - it cannot be decorative). Write Verify
> lines in the **DSL** (`jest <pattern>` / `pytest <node>` / `http METHOD URL -- <jq>` /
> `manual <what>`) against the project's real runner, never free-form `npm test -- ... -t` or
> `curl ... returns N` (those fall through to `shell` and silently fail); `verify_ac lint`
> flags those at author time. Env-bound ACs use `http` or `manual`, not raw `curl`/`psql`.

Acceptance criteria in story files can declare a `Verify:` expression
that `/sdlc-studio reconcile --verify` executes against the live
codebase. Each AC gains a machine-maintained `Verified:` state so the
skill can report real, continuously-validated status instead of
trusting manual checkbox ticks that drift from reality.

<!-- Load when: writing ACs with verifiers, running reconcile --verify, or adopting the require_ac_verification gate -->

## Reading Guide

| Section | When to Read |
| --- | --- |
| Why It Exists | When deciding whether to add verifiers to a story |
| AC Format | When authoring or generating stories |
| Verifier DSL | When writing a Verify expression |
| Writing Good Verifiers | When a verifier flakes or is hard to maintain |
| Running | When invoking reconcile --verify |
| Report Format | When consuming the verify-report.json file |
| Gated Completion | When enabling require_ac_verification |
| Troubleshooting | When a verifier is failing unexpectedly |

## Why It Exists {#verify-why}

Through v1.5.0, acceptance criteria were Given/When/Then markdown
with no executable backing. Teams ticked manual checkboxes during
review and trusted that stories marked Done actually met their ACs.
Production runs showed this trust erodes within a week: ticked ACs
regress when downstream changes break the original assumption.

Executable ACs close this gap. A verifier is a one-line shell
expression that can be mechanically re-run any time. Reconcile walks
every story, runs each verifier, and updates a `Verified:` state.
Status dashboards stop lying because the state is derived, not
asserted.

Verifiers are optional. Every AC can still be verified manually by
leaving the `Verify:` line off. The opt-in nature lets teams adopt
incrementally.

## AC Format {#verify-ac-format}

The story template accepts two new optional bullet lines per AC:

```markdown
### AC1: Happy path email login
- **Given** a registered account
- **When** the user submits valid credentials
- **Then** they are redirected to /dashboard
- **Verify:** pytest tests/unit/auth/test_login.py::test_email_happy
- **Verified:** yes (2026-04-15)
```

Rules:

- **Verify:** line is author-maintained. Missing line means manual
  verification (reconcile leaves the AC untouched).
- **Verified:** line is machine-maintained by `verify_ac.py`. Values:
  `yes`, `no`, `stale`, `manual`. The date in parentheses records
  the last run.
- Indentation must match the other `- **Field:**` bullets in the AC.
- Order within the AC: Given / When / Then / Verify / Verified.
- New ACs added by `story create` or `cr action` ship with
  `Verified: no` until reconcile runs.

## Verifier DSL {#verify-dsl}

One expression per AC. The first token is a type prefix; the rest is
interpreted in that type's semantics. Anything unrecognised falls
back to `shell`.

| Prefix | Semantics | Example |
| --- | --- | --- |
| `pytest <node>` | `pytest -q <node>`, pass on exit 0 | `pytest tests/test_auth.py::test_email` |
| `jest <pattern>` | `jest -t <pattern>`, pass on exit 0 | `jest "login happy path"` |
| `vitest <pattern>` | `vitest run -t <pattern>` | `vitest "submits form"` |
| `go <args>` | `go test <args>` | `go ./internal/auth -run TestLogin` |
| `file <path>` | File must exist (`test -e`) | `file src/auth/email.ts` |
| `grep <regex> <path>` | `rg -q` (or `grep -rqE`) must match | `grep "export class AuthClient" src/**/*.ts` |
| `http METHOD URL -- <jq>` | curl + jq assertion | `http GET /health -- .status == "ok"` |
| `eval <cmd> --threshold <f>` | run a graded eval tool; pass when its JSON `{"score": f}` >= threshold | `eval promptfoo eval -c judge.yaml --threshold 0.8` |
| `shell <cmd>` | Arbitrary shell, pass on exit 0 | `shell test -f dist/bundle.js` |

**The `grep` verb.** The path may be a glob (`src/**/*.ts`); it is expanded against the run
directory before the tool sees it, so the documented example matches present code (an unmatched
glob passes through literally, giving an honest not-found). The engine is ripgrep when present,
else `grep -rqE` - **different regex dialects** (Rust regex vs POSIX ERE). For a verdict that is
identical everywhere, keep `grep` patterns POSIX-ERE-portable (avoid `\d`, `\w`, `\b`, lookahead)
or install ripgrep so every host uses the same engine.

The `http` form builds a pipeline equivalent to:

```bash
curl -sf -X METHOD URL | jq -e '<jq_expr>' > /dev/null
```

Use `http` for ACs that depend on a running service (dev server,
staging). Use `file` for simple existence checks. Use `grep` when
you want the AC to fail if a key symbol disappears. Use the
test-framework prefixes (`pytest`, `jest`, `vitest`, `go`) for
behavioural assertions that already have test coverage.

Shell commands run with `cwd` set to `--repo-root` (default: current
directory). Every verifier has a `--timeout` limit (default 120s).

## Writing Good Verifiers {#verify-writing-good}

**Keep them deterministic.** A verifier that depends on the wall
clock, network latency, or external state will flake. If you need
timing, use a mocked clock inside the test framework and call it
with `pytest`/`jest` instead of `shell sleep`.

**Make them fast.** The verifier runs on every reconcile. A slow
verifier becomes a reconcile bottleneck. Target sub-second for
`file`/`grep`, under 5 seconds for `pytest -q` on a single test.

**Prefer narrow scope.** `pytest tests/test_auth.py::test_email`
is better than `pytest tests/test_auth.py` because a failure in
another test in the same file will fail the AC spuriously.

**Name tests after ACs.** When AC1 maps to
`test_ac1_email_happy_path`, the verifier is trivial to write and
the failure is trivial to diagnose.

**Mirror the AC intent, not the implementation.** `grep` that
matches a class name is brittle because renames break it. A
behavioural test that imports the class and exercises it is
stable.

**Use `shell` sparingly.** The `shell` verb exists for cases the DSL
doesn't cover (`docker compose ps`, `kubectl get`, custom probe
binaries). If you find yourself writing multi-line shell
expressions, push the logic into a test file and use `pytest`. An
unrecognised expression is **not** run as a shell command - it is an
invalid verifier (exit 2). Prefix an explicit `shell` to run one, or
pass `--allow-shell-fallback` for the legacy behaviour.

**Trust boundary (enforced, not just documented).** `verify_ac.py` runs
`shell`/`eval`/`http` verifiers through the shell. The trust model is
that `Verify:` lines are authored by the team alongside the story. That
assumption breaks the moment a story body is ingested from an external
source - a GitHub issue pulled via `github_sync pull`, for example. Two
technical controls back the rule so it is not procedure-only:

- **Provenance stamp.** A story carrying `> **Provenance:** external` in
  its metadata will not have its shell-backed verifiers executed;
  they report `blocked`, not run. The ingest path stamps this field
mechanically (`artifact.py new --provenance external`, mandated by the
from-issue branches of the CR and story workflows), so
  un-reviewed external content cannot reach a shell just because a
  workflow copied it into a story. Clear or change the stamp only after
  review; pass `--allow-external` to override deliberately.
- **`--no-shell` mode.** Restricts a run to the structured DSL verbs
  (argv, no shell) for CI over less-trusted content.

**Allow-list the `http` hosts on a cloud or CI runner.** The `http` verb enforces an
http/https scheme floor in every mode, but its host allow-list is opt-in: with
`SDLC_VERIFY_HTTP_HOSTS` unset (the default) any http/https host is reachable, including
a cloud link-local metadata endpoint (`169.254.169.254`). That sits inside the trust
boundary above - Verify lines are team-authored - but on a host that holds credentials,
set the allow-list so a well-intentioned-but-mistaken Verify line cannot reach a metadata
service:

```bash
export SDLC_VERIFY_HTTP_HOSTS=localhost,127.0.0.1,staging.example.com
```

A target host outside the list is refused as an invalid verifier (exit 2), as is a
relative URL (it has no host).

**Still: never run verifiers on a story whose AC block came from
un-reviewed external content.** Ingest the body into the template,
review it, clear the provenance stamp, then verify.

## Running {#verify-running}

**Interactive:**

```text
/sdlc-studio reconcile --verify                  # All stories
/sdlc-studio reconcile --verify --story US0001   # Single story
/sdlc-studio reconcile --verify --dry-run        # Preview, no writes
```

Under the hood, Claude invokes:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/verify_ac.py" run \
  [--dir sdlc-studio/stories] \
  [--story <path>] \
  [--dry-run] \
  [--timeout 120] \
  [--repo-root .]
```

**Automatic:** `verify_ac.py` runs automatically in two situations:

1. **`reconcile --scope verify`**: explicit scope filter for CI
   pipelines that only want verification state updated
2. **Story Completion Cascade** (if `require_ac_verification: true`
   in config): Step 10 refuses to mark a story Done unless all ACs
   have `Verified: yes`

## Batch verification {#batch}

`reconcile --verify --batch` runs **jest once** (`jest --json`) and resolves every
jest-targeted AC against that single result set, instead of a cold `jest -t` start per AC - a field
sprint measured ~48 cold starts / 70s collapsing to one run. A jest pattern passes iff at least one
assertion name contains it and all matching pass (mirroring `jest -t`); anything not found in the
cache falls through to the authoritative per-AC subprocess, as do non-jest verbs
(`pytest`/`vitest`/`file`/`grep`/`http`/`shell`/`manual`). pytest and vitest batch caches are a
fast-follow - the parse/resolve path is runner-general; only the per-runner cache producer is
jest-specific today.

## Report Format {#verify-report}

Written to `sdlc-studio/.local/verify-report.json` after every apply
run. Each run **merges** its stories into the report (this run's entries win, others are
preserved), so verifying a sprint one story at a time accumulates and the Done-gate finds
every verified story - you need not re-run the whole `--dir` to populate it. Use `--fresh` to
rebuild from the current run only. The `report` subcommand prints it in text or JSON:

```text
/sdlc-studio reconcile --verify report
/sdlc-studio reconcile --verify report --format json
```

Shape:

```json
{
  "generated_at": "2026-04-15T12:34:56Z",
  "stories": {
    "US0001-login": {
      "ac_count": 5,
      "verified": 3,
      "failed": 1,
      "stale": 1,
      "manual": 0,
      "passed": ["AC1", "AC2", "AC3"],
      "failures": [
        {
          "ac": "AC4",
          "verifier": "pytest tests/test_auth.py::test_locked_account",
          "kind": "pytest",
          "exit_code": 1,
          "stderr": "AssertionError: expected 423, got 200",
          "duration_ms": 812
        }
      ]
    }
  }
}
```

Counts:

- `ac_count`: total ACs in the story
- `verified`: ACs that passed their verifier in this run
- `failed`: ACs whose verifier returned non-zero
- `stale`: ACs whose Verified state was downgraded this run
- `manual`: ACs without a Verify line (reconcile did not run one)

## Gated Completion {#verify-gate}

Set `require_ac_verification: true` in `templates/config-defaults.yaml`
or the project-local `sdlc-studio/config.yaml` to prevent a story
from transitioning to Done unless every AC reports `Verified: yes`.

Default is `false` for backwards compatibility. Teams adopting the
verifier workflow should leave the flag off while seeding `Verify:`
lines across their existing stories, then flip it once reconcile
reports `manual: 0` for the whole repository.

When the gate is on, the Story Completion Cascade in
`reference-outputs.md#story-completion-cascade` runs an extra
pre-flight verifier step before step 10 (index and cascade updates).
A story that fails the gate stays In Progress with a report pointing
at the failing ACs.

### Freshness: what invalidates a green result

A green verification is judged fresh by an **AC fingerprint** - a hash of each AC's
id, title and `Verify:` command - not by the story file's modification time. mtime
answers "was the file touched", not "did what we verified change": a status
transition, a revision-history row, or the `- **Verified:**` stamps the verifier
itself writes all move mtime while leaving every AC and verifier untouched, and
each used to force a re-run that could only produce the same result.

So a re-verify is demanded when an AC is added, removed, retitled, or its verifier
re-pointed - and not otherwise. Deliberately outside the fingerprint: **prose inside
an AC body** (the `Given`/`When`/`Then` narrative). Editing that changes what the AC
*means* to a reader without changing what the verifier *executes*, so the mechanical
gate cannot judge it. Semantic drift between an AC's prose and its verifier is the
reviewer's call, not the fingerprint's - which is one reason the critic pass is a
separate gate. Reports written before the fingerprint existed carry none and still
fall back to mtime, so its absence never silently passes a stale green.

## Troubleshooting {#verify-trouble}

**`kind: invalid, exit_code: 2`**: The verifier expression could not
be parsed. Check the DSL table for the expected syntax. Common
mistakes: `http` without ` -- ` separator, `grep` without both
pattern and path.

**`kind: <anything>, exit_code: 127`**: The underlying tool is not
on PATH. Install `pytest`, `jest`, `rg`, `curl`, `jq` as needed.

**`kind: <anything>, exit_code: 124`**: Timeout. Either the verifier
is slow (raise `--timeout`) or the process is hanging (add proper
teardown in the test).

**Verifier passes locally, fails in CI**: The `--repo-root` cwd in
CI may differ from the dev machine. Always use paths relative to the
repo root, never to the story file.

**Repeatedly downgrading yes -> no**: The verifier is flaky. See
"Writing Good Verifiers" above. If the test is correct but the
service under test is unstable, move the AC verification to
`pytest` with explicit retries.

## See Also

- `scripts/verify_ac.py` - The implementation
- `reference-reconcile.md#verify-scope` - How reconcile wires the runner in
- `reference-outputs.md#story-completion-cascade` - The gated completion flow
- `reference-story.md#story-workflow` - Story generation emits best-effort Verify lines
- `templates/core/story.md` - Template AC format with Verify/Verified placeholders
- `help/verify.md` - User-facing help
- `templates/config-defaults.yaml` - The require_ac_verification flag
