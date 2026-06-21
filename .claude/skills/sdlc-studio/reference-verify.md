# SDLC Studio Reference - Executable Acceptance Criteria

> **Human-checked ACs:** author the Verify line as `Verify: manual <what to check>`. A line led
> by `manual` (or `manually`) is counted **manual** - never executed - so a prose check can't be
> shelled out and time out into a false `failed`.

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

**Use `shell` sparingly.** The fallback exists for cases the DSL
doesn't cover (`docker compose ps`, `kubectl get`, custom probe
binaries). If you find yourself writing multi-line shell
expressions, push the logic into a test file and use `pytest`.

**Trust boundary (important).** `verify_ac.py` runs `shell` verifiers
through the shell, and any unrecognised expression falls back to
`shell`. The trust model is that `Verify:` lines are authored by the
team alongside the story. That assumption breaks the moment a story
body is ingested from an external source - a GitHub issue pulled via
`github_sync pull`, for example. **Never run verifiers on a story whose
AC block came from un-reviewed external content.** Ingest the body into
the template, review it, then verify.

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

## Report Format {#verify-report}

Written to `sdlc-studio/.local/verify-report.json` after every apply
run. The `report` subcommand prints it in text or JSON:

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
