#!/bin/bash
# Run a test suite and write its verdict where it can be READ, not interpreted.
# Usage: tools/run-suite.sh scripts|tools|all
#
# `npm test 2>&1 | tail -15` reports TAIL's exit status, not the suite's. The runners set
# `set -uo pipefail`; the ad-hoc shell that invokes them does not. That cost two false claims
# in one session - a commit reported as landed when the hook had refused it, and a suite
# reported green with a real failure in it.
#
# Telling people to be careful does not fix it: the pipe is there because a six-minute suite's
# output does not fit in one read, so the incentive comes back every run. This prints ONE line
# and writes the verdict to sdlc-studio/.local/suite-verdict.json, so the question "was it
# green" is answered by reading a field instead of interpreting a stream.
#
# The verdict is written on FAILURE as well as success, and deliberately overwrites: a wrapper
# that skipped the write on a red run would leave the previous GREEN verdict in place, which is
# worse than none because it is stale and looks current.

set -uo pipefail

# The root is resolved from where the script was INVOKED, not from where it lives. Anchoring
# to the script's own directory means a run inside another checkout - a worktree, a fixture -
# writes its verdict into the source tree instead, so the file would describe a suite that was
# never run there. Caught by this script's own tests writing into the real repo.
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
VERDICT_REL="sdlc-studio/.local/suite-verdict.json"

usage() {
    cat <<'EOF'
Usage: tools/run-suite.sh scripts|tools|all

Runs a suite, prints one verdict line, and writes the full verdict to
sdlc-studio/.local/suite-verdict.json:

  {suite, exit_code, passed, failed, duration, head_sha}

Exits with the SUITE's status, so a caller that checks $? is still correct.
Read the file rather than the output - that is the point.

Options:
  --help, -h    Show this help
EOF
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    usage; exit 0
fi

# --check is the half that makes the verdict load-bearing. Writing a verdict nobody reads
# changes nothing; this turns "I ran the suite" from a claim into a fact a gate can refuse.
if [[ "${1:-}" == "--check" ]]; then
    cd "$PROJECT_ROOT" || exit 2
    if [[ ! -f "$VERDICT_REL" ]]; then
        # ABSENT never reads as green. That is the fail-open shape, and it is exactly the
        # state - a suite that was never run - the check exists to catch.
        echo "run-suite --check: no suite verdict at $VERDICT_REL - run 'tools/run-suite.sh all' " \
             "before claiming the suite is green" >&2
        exit 1
    fi
    V_RC="$(grep -oE '"exit_code":[[:space:]]*-?[0-9]+' "$VERDICT_REL" | grep -oE '\-?[0-9]+' || echo missing)"
    V_SHA="$(grep -oE '"head_sha":[[:space:]]*"[^"]*"' "$VERDICT_REL" | sed 's/.*"\([^"]*\)"$/\1/' || echo missing)"
    HEAD_NOW="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
    if [[ "$V_SHA" != "$HEAD_NOW" ]]; then
        echo "run-suite --check: the suite verdict is STALE - taken at ${V_SHA:0:12}, HEAD is " \
             "${HEAD_NOW:0:12}. A verdict from an earlier commit exists and looks current, " \
             "which is worse than none. Re-run the suite." >&2
        exit 1
    fi
    if [[ "$V_RC" != "0" ]]; then
        echo "run-suite --check: the recorded verdict is RED (exit $V_RC) at this HEAD" >&2
        exit 1
    fi
    echo "suite verdict: GREEN at ${HEAD_NOW:0:12}"
    exit 0
fi

SUITE="${1:-}"
case "$SUITE" in
    scripts) CMD='python3 -B -m pytest .claude/skills/sdlc-studio/scripts/tests -q' ;;
    tools)   CMD='PYTHONPATH=tools/tests python3 -B -m unittest discover -s tools/tests' ;;
    all)     CMD='python3 -B -m pytest .claude/skills/sdlc-studio/scripts/tests -q && PYTHONPATH=tools/tests python3 -B -m unittest discover -s tools/tests' ;;
    *)
        # REFUSED, never defaulted. Running a different suite and reporting it under the
        # requested name is a false green of exactly the kind this script exists to remove,
        # and no verdict is written - an absent verdict is honest, a wrong one is not.
        echo "run-suite: unknown suite ${SUITE:-<none>} - expected scripts, tools or all" >&2
        usage >&2
        exit 2
        ;;
esac

# FOR THE TESTS. A test that shelled out to the real six-minute suite to check this script's
# bookkeeping could not run in a suite itself; one that mocked the script entirely would test
# nothing. Documented rather than hidden, because an undocumented env hook is a trapdoor.
CMD="${SUITE_CMD_OVERRIDE:-$CMD}"

cd "$PROJECT_ROOT" || exit 2
mkdir -p "$(dirname "$VERDICT_REL")"

OUT="$(mktemp)"
trap 'rm -f "$OUT"' EXIT

START="$(date +%s)"
# Bytecode is purged so a same-length mutant cannot be served from a cached .pyc - the false
# SURVIVED this repo has been bitten by before.
find . -name "__pycache__" -not -path "./node_modules/*" -not -path "./.claude/worktrees/*" \
    -exec rm -rf {} + 2>/dev/null
bash -c "$CMD" >"$OUT" 2>&1
RC=$?
DURATION=$(( $(date +%s) - START ))

# Counts are best-effort across two runners with different report lines; an unparseable count
# is recorded as null rather than 0, because "not stated" and "none" are different facts.
PASSED="$(grep -oE '([0-9]+) passed' "$OUT" | tail -1 | grep -oE '[0-9]+' || true)"
FAILED="$(grep -oE '([0-9]+) failed' "$OUT" | tail -1 | grep -oE '[0-9]+' || true)"
if [[ -z "$PASSED" ]]; then
    PASSED="$(grep -oE '^Ran ([0-9]+) tests' "$OUT" | tail -1 | grep -oE '[0-9]+' || true)"
fi
[[ -z "$PASSED" ]] && PASSED=null
[[ -z "$FAILED" ]] && FAILED=null

HEAD_SHA="$(git rev-parse HEAD 2>/dev/null || echo unknown)"

cat > "$VERDICT_REL" <<EOF
{
  "suite": "$SUITE",
  "exit_code": $RC,
  "passed": $PASSED,
  "failed": $FAILED,
  "duration": $DURATION,
  "head_sha": "$HEAD_SHA"
}
EOF

if [[ $RC -eq 0 ]]; then
    echo "suite $SUITE: GREEN (${PASSED} passed, ${DURATION}s) -> $VERDICT_REL"
else
    # The tail of the output goes to STDERR on failure only: a red run is the one time the
    # detail is worth seeing, and stderr keeps stdout to the single verdict line.
    echo "suite $SUITE: RED (exit $RC, ${DURATION}s) -> $VERDICT_REL"
    tail -25 "$OUT" >&2
fi
exit $RC
